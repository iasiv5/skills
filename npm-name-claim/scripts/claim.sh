#!/usr/bin/env bash
# claim.sh — npm 包名抢注与无 token 发版工具（查名 / 搭占位包 / 免贴token认证 / 伪TTY发布 / 验证 / 清理 / OIDC信任）
# 依赖: bash, curl, node, npm, script(util-linux)
# 用法: claim.sh <check|scaffold|weblogin|publish|verify|cleanup|trust> ...
set -euo pipefail

REGISTRY="https://registry.npmjs.org"
USAGE="用法:
  claim.sh check <name>                                   查可用性+合规+近似名
  claim.sh scaffold <name> [--dir BASE] [--desc T] [--repo URL] [--homepage URL] [--author N]
                                                          搭 0.0.1 占位包到 BASE/<name>（默认 ./npm-packages）
  claim.sh weblogin <pkgdir>                              web 登录拿 token 写入 <pkgdir>/.npmrc（token 不回显）
  claim.sh publish <pkgdir>                               伪 TTY 发布；EOTP 时输出 AUTH_URL 交用户授权，之后自动完成
  claim.sh verify <name>                                  验证已发布（200 + 版本 + 发布者）
  claim.sh cleanup <pkgdir>                               删除包目录里的 .npmrc（token 卫生）
  claim.sh trust <pkgdir> --repo OWNER/REPO --file <workflow.yml> [--allow-publish]
                                                          配 GitHub Actions OIDC 信任（npm trust github）；EOTP 时输出 AUTH_URL"

die() { echo "ERROR: $*" >&2; exit 1; }
jsonget() { node -e "const d=JSON.parse(process.argv[1]); const ks=process.argv[2].split('.'); let v=d; for(const k of ks) v=v?.[k]; console.log(v ?? '')" "$1" "$2"; }

cmd="${1:-}"; shift || true
case "$cmd" in

check)
  name="${1:-}" ; [ -n "$name" ] || die "$USAGE"
  # 名字合规（新包规则：小写字母数字连字符，可带 scope，不以点/下划线开头，≤214）
  if [[ "$name" =~ ^@ ]]; then
    [[ "$name" =~ ^@[a-z0-9-]+/[a-z0-9][a-z0-9-]*$ ]] || die "scope 包名不合规: $name"
  else
    [[ "$name" =~ ^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$ ]] || die "包名不合规（需小写字母/数字/连字符，且不以连字符开头结尾）: $name"
  fi
  [ ${#name} -le 214 ] || die "包名超过 214 字符"
  code=$(curl -s -o /dev/null -w '%{http_code}' "$REGISTRY/$name")
  case "$code" in
    404) echo "AVAILABLE: $name 未注册，可抢注" ;;
    200) echo "TAKEN: $name 已被注册" ;;
    *)   die "registry 返回 HTTP $code，请人工确认" ;;
  esac
  enc=${name//@/%40} ; enc=${enc//\//%2F}
  echo "--- 近似名（评估混淆/typosquat 争议风险）---"
  curl -s "$REGISTRY/-/v1/search?text=$enc&size=5" \
    | node -e "let s='';process.stdin.on('data',c=>s+=c).on('end',()=>{const d=JSON.parse(s);for(const o of d.objects)console.log(' ', o.package.name, '|', o.package.version, '|', (o.package.description||'').slice(0,70))})"
  ;;

scaffold)
  name="${1:-}" ; [ -n "$name" ] || die "$USAGE" ; shift || true
  base="./npm-packages" ; desc="" ; repo="" ; homepage="" ; author=""
  while [ $# -gt 0 ]; do case "$1" in
    --dir) base="$2"; shift 2;; --desc) desc="$2"; shift 2;; --repo) repo="$2"; shift 2;;
    --homepage) homepage="$2"; shift 2;; --author) author="$2"; shift 2;;
    *) die "未知参数: $1";; esac; done
  dir="$base/$name" ; mkdir -p "$dir"
  [ -f "$dir/package.json" ] && die "$dir/package.json 已存在，先确认再手动处理"
  node -e '
    const [name, desc, repo, homepage, author, dir] = process.argv.slice(1);
    const pkg = {
      name, version: "0.0.1",
      description: desc || `${name} placeholder release to reserve the package name.`,
      license: "MIT", author: author || "",
      ...(homepage ? { homepage } : {}),
      ...(repo ? { repository: { type: "git", url: "git+" + repo } } : {}),
      keywords: [],
      main: "index.js", files: ["index.js", "README.md"],
      engines: { node: ">=18" },
      publishConfig: { registry: "https://registry.npmjs.org/" },
    };
    require("fs").writeFileSync(dir + "/package.json", JSON.stringify(pkg, null, 2) + "\n");
  ' "$name" "$desc" "$repo" "$homepage" "$author" "$dir"
  cat > "$dir/index.js" <<EOF
// $name — placeholder package (name reservation)
module.exports = { name: '$name', version: '0.0.1' };
EOF
  cat > "$dir/README.md" <<EOF
# $name

**占位包（placeholder）**：用于保留 \`$name\` 这个 npm 包名。
$([ -n "$homepage" ] && echo "
- 项目主页：<$homepage>")$([ -n "$repo" ] && echo "
- 源码仓库：<$repo>")

> Placeholder release reserving the \`$name\` name on npm. Do not depend on
> \`0.0.x\` versions.
EOF
  # 打包自检（cache/logs 指到 base 下，规避只读 ~/.npm 的静默崩溃）
  cache="$base/.npm-cache"; logs="$base/.npm-logs"; mkdir -p "$cache" "$logs"
  if (cd "$dir" && npm pack --dry-run --cache "$cache" --logs-dir "$logs" >/dev/null 2>&1); then
    echo "SCAFFOLDED: $dir （打包自检通过）"
  else
    echo "SCAFFOLDED: $dir （注意：打包自检失败，运行 npm pack --dry-run 看详情）"
  fi
  ;;

weblogin)
  pkgdir="${1:-}"; [ -n "$pkgdir" ] && [ -d "$pkgdir" ] || die "$USAGE"
  pkgdir=$(cd "$pkgdir" && pwd)
  resp=$(curl -s -X POST "$REGISTRY/-/v1/login" \
    -H "content-type: application/json" -H "npm-auth-type: web" -d '{}')
  loginUrl=$(jsonget "$resp" loginUrl) ; doneUrl=$(jsonget "$resp" doneUrl)
  [ -n "$loginUrl" ] && [ -n "$doneUrl" ] || die "registry 未返回登录会话: $resp"
  echo "LOGIN_URL: $loginUrl"
  echo "等待用户在浏览器完成授权（最多 5 分钟）..."
  tmp=$(mktemp) ; ok=""
  for i in $(seq 1 150); do
    code=$(curl -s -o "$tmp" -w '%{http_code}' -H "accept: application/json" "$doneUrl" || echo 000)
    if [ "$code" = "200" ]; then ok=1; break; fi
    sleep 2
  done
  [ -n "$ok" ] || { rm -f "$tmp"; die "超时：用户未在 5 分钟内完成授权，请重新运行 weblogin"; }
  token=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$tmp','utf8')).token||'')")
  rm -f "$tmp"; [ -n "$token" ] || die "doneUrl 返回 200 但无 token"
  printf '//registry.npmjs.org/:_authToken=%s\n' "$token" > "$pkgdir/.npmrc"
  chmod 600 "$pkgdir/.npmrc"
  echo "OK: token 已写入 $pkgdir/.npmrc（length=${#token}，明文不回显）"
  ;;

publish)
  pkgdir="${1:-}"; [ -n "$pkgdir" ] && [ -d "$pkgdir" ] || die "$USAGE"
  pkgdir=$(cd "$pkgdir" && pwd)
  base=$(dirname "$pkgdir") ; cache="$base/.npm-cache" ; logs="$base/.npm-logs"
  mkdir -p "$cache" "$logs"
  ts="$logs/publish-$(basename "$pkgdir")-$(date +%s).out"
  name=$(jsonget "$(cat "$pkgdir/package.json")" name)
  version=$(jsonget "$(cat "$pkgdir/package.json")" version)
  # 认证预检：无包级 .npmrc 时看全局凭证是否可用
  if [ ! -f "$pkgdir/.npmrc" ]; then
    (cd "$pkgdir" && npm whoami --registry "$REGISTRY" --cache "$cache" --logs-dir "$logs" >/dev/null 2>&1) \
      || die "未认证：先运行 claim.sh weblogin $pkgdir，或在 $pkgdir/.npmrc 放入 //registry.npmjs.org/:_authToken"
  fi
  echo "PUBLISHING: $name@$version （账号启用 2FA 时会输出 AUTH_URL，请转交用户授权；npm 会自动继续）"
  # 伪 TTY 让 otplease 走 web-OTP；--browser=false 让 opener 只打印真实授权链接（不脱敏、不弹浏览器、不等回车）
  set +e
  # 必须在包目录内执行：npm 以 cwd 的 package.json 为发布目标
  script -qec "cd '$pkgdir' && npm publish --access public --browser=false --registry $REGISTRY --cache $cache --logs-dir $logs" "$ts" &
  spid=$!
  url=""
  while kill -0 "$spid" 2>/dev/null; do
    if [ -z "$url" ] && [ -s "$ts" ]; then
      url=$(tr -d '\r' < "$ts" | grep -oE 'https://www\.npmjs\.com/auth/cli/[a-z0-9-]+' | tail -1 || true)
      [ -n "$url" ] && echo "AUTH_URL: $url"
    fi
    sleep 2
  done
  wait "$spid"; rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    echo "PUBLISHED: $name@$version （可用 claim.sh verify $name 复核）"
  elif [ -n "$url" ]; then
    echo "FAILED(EOTP): 授权链接未被完成或已过期，重新运行本命令重试: $url" ; exit 1
  else
    echo "FAILED: 发布失败，输出末尾如下：" ; tr -d '\r' < "$ts" | tail -15 ; exit 1
  fi
  ;;

trust)
  pkgdir="${1:-}"; [ -n "$pkgdir" ] && [ -d "$pkgdir" ] || die "$USAGE"
  shift || true
  repo="" ; file="" ; allow=""
  while [ $# -gt 0 ]; do case "$1" in
    --repo|--repository) repo="${2:-}"; shift 2;;
    --file) file="${2:-}"; shift 2;;
    --allow-publish) allow="--allow-publish"; shift;;
    *) die "未知参数: $1";; esac; done
  [ -n "$repo" ] && [ -n "$file" ] || die "trust 需要 --repo OWNER/REPO 与 --file <workflow 文件名>"
  pkgdir=$(cd "$pkgdir" && pwd)
  base=$(dirname "$pkgdir") ; cache="$base/.npm-cache" ; logs="$base/.npm-logs"
  mkdir -p "$cache" "$logs"
  ts="$logs/trust-$(basename "$pkgdir")-$(date +%s).out"
  name=$(jsonget "$(cat "$pkgdir/package.json")" name)
  # 前提：包必须已存在（0.0.1 bootstrap 已覆盖；首发无法直接 OIDC，见 npm/cli#8544）。
  echo "TRUST: $name ← github $repo :: $file $allow （2FA 账号必走 AUTH_URL，请转交用户授权；npm 会自动继续）"
  # 两个坑（2026-09-18 实战）：
  # 1) npm trust 的子命令解析器不认 --cache/--logs-dir/--browser 这类空格分隔的全局 flag，
  #    值会被当成多余的位置参数（Unknown positional argument）→ 一律走 npm_config_* 环境变量；
  # 2) trust 连 list 读操作都触发 EOTP，且错误通道里授权链接打码 → 伪 TTY + browser=false
  #    让明文 AUTH_URL 走 stdout，npm 拿到 OTP 票据后自动重试。
  set +e
  script -qec "cd '$pkgdir' && npm_config_browser=false npm_config_cache='$cache' npm_config_logs_dir='$logs' npm trust github '$name' --repository '$repo' --file '$file' $allow -y --registry $REGISTRY" "$ts" &
  spid=$!
  url=""
  while kill -0 "$spid" 2>/dev/null; do
    if [ -s "$ts" ]; then
      u=$(tr -d '\r' < "$ts" | grep -oE 'https://www\.npmjs\.com/auth/cli/[a-z0-9-]+' | tail -1 || true)
      [ -n "$u" ] && [ "$u" != "$url" ] && { url="$u"; echo "AUTH_URL: $url"; }
    fi
    sleep 2
  done
  wait "$spid"; rc=$?
  set -e
  if [ "$rc" -eq 0 ] && tr -d '\r' < "$ts" | grep -q "Trust configuration created"; then
    echo "TRUSTED: $name ↔ $repo :: $file （npm trust list 可复核）"
  elif [ -n "$url" ]; then
    echo "FAILED(EOTP): 授权链接未被完成或已过期，重新运行本命令重试: $url" ; exit 1
  else
    echo "FAILED: trust 配置失败，输出末尾如下：" ; tr -d '\r' < "$ts" | tail -15 ; exit 1
  fi
  ;;

verify)
  name="${1:-}"; [ -n "$name" ] || die "$USAGE"
  code=$(curl -s -o /dev/null -w '%{http_code}' "$REGISTRY/$name")
  [ "$code" = "200" ] || die "$name -> HTTP $code（尚未生效？registry 有分钟级缓存）"
  curl -s "$REGISTRY/$name" | node -e "
    let s='';process.stdin.on('data',c=>s+=c).on('end',()=>{const d=JSON.parse(s);
    const v=d.versions[d['dist-tags'].latest];
    console.log('LIVE:', d.name+'@'+d['dist-tags'].latest, '| by', (v._npmUser||{}).name, '| https://www.npmjs.com/package/'+d.name)})"
  ;;

cleanup)
  pkgdir="${1:-}"; [ -n "$pkgdir" ] || die "$USAGE"
  if [ -f "$pkgdir/.npmrc" ]; then rm -f "$pkgdir/.npmrc" && echo "CLEANED: 已删除 $pkgdir/.npmrc"
  else echo "无 .npmrc，无需清理"; fi
  ;;

*)
  echo "$USAGE" ; [ -z "$cmd" ] && exit 0 || exit 1 ;;
esac
