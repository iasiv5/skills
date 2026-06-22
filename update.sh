#!/usr/bin/env bash
# update.sh — 从 GitHub 更新 skills（覆盖旧版本，旧版本备份到 .backup/<skill>/）
# 用法:
#   ./update.sh              # 更新 .your-skill-collection.json 中所有 skills
#   ./update.sh docx pdf     # 只更新指定的 skills
# 注意: skip 列表中的 skill 不参与更新

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$(command -v cygpath >/dev/null 2>&1 && cygpath -w "$SKILLS_DIR" || echo "$SKILLS_DIR")"
TMP_BASE=$(mktemp -d)
trap 'rm -rf "$TMP_BASE"' EXIT

command -v python3 >/dev/null 2>&1 || { echo "错误: 需要 python3"; exit 1; }
command -v git     >/dev/null 2>&1 || { echo "错误: 需要 git";     exit 1; }

log()  { printf '\033[34m▶\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m✓ 已更新\033[0m\n'; }
warn() { printf '    \033[33m⊘\033[0m %s\n' "$*"; }
fail() { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; }

FILTER="${*:-}"

# 主源（默认 github.com）与镜像兜底源。镜像源可用环境变量覆盖，不写死本机设定：
#   GITHUB_MIRROR=https://gh-proxy.com/https://github.com ./update.sh
# 每次启动都从主源 github 开始试（切换标志存于临时目录 $TMP_BASE，随脚本退出自动清除）；只有判定 github 不可达才切镜像。
BASE="${GITHUB_BASE_URL:-https://github.com}"
MIRROR="${GITHUB_MIRROR:-https://gh-proxy.com/https://github.com}"
CLONE_ERR="$TMP_BASE/.clone_err"

# 低速保护克隆：60 秒内收不到数据（=连不上/没开始）即判失败，stderr 落到 $CLONE_ERR 供判定
clone_url() {  # $1=base $2=repo(owner/name) $3=dest
  git -c http.lowSpeedLimit=1 -c http.lowSpeedTime=60 -c http.connectTimeout=60 \
    clone --depth=1 --quiet "$1/$2.git" "$3" 2>"$CLONE_ERR"
}

# 判定上次 clone 失败是否属于网络层（连不上/卡住）→ 此类才值得切镜像；
# 秒退类失败（仓库不存在等）镜像也救不了，不切。
is_net_failure() {  # $1=本次耗时(s)
  local err; err=$(cat "$CLONE_ERR" 2>/dev/null || true)
  (( ${1:-0} >= 50 )) && return 0
  [[ "$err" =~ (timed[[:space:]]out|Connection[[:space:]]timed[[:space:]]out|early[[:space:]]EOF|RPC[[:space:]]failed|Could[[:space:]]not[[:space:]]resolve[[:space:]]host|Connection[[:space:]]refused|Connection[[:space:]]reset|Failed[[:space:]]to[[:space:]]connect|unable[[:space:]]to[[:space:]]access|Empty[[:space:]]reply) ]]
}

# 克隆仓库到临时目录（同一仓库只克隆一次）
# 默认先试 github 主源；若判定为网络不可达，提示并切换镜像，本次运行后续都直接走镜像。
# 注意：本函数在命令替换 $(get_clone) 的子 shell 中被调用，故——
#   1) 切镜像状态用文件标志 $TMP_BASE/.use_mirror（跨子 shell 持久，变量传不回父 shell）；
#   2) 所有提示一律输出到 stderr，避免污染被捕获的 stdout（=仓库路径）。
get_clone() {
  local repo="$1"
  local dest="$TMP_BASE/${repo//\//__}"
  [[ -d "$dest" ]] && { printf '%s' "$dest"; return 0; }

  # 本次运行已确认 github 不可达 → 直接走镜像
  if [[ -f "$TMP_BASE/.use_mirror" ]]; then
    if clone_url "$MIRROR" "$repo" "$dest"; then printf '%s' "$dest"; return 0; fi
    rm -rf "$dest"; fail "镜像克隆失败: $repo"; return 1
  fi

  # 默认先试 github 主源
  local start=$SECONDS
  if clone_url "$BASE" "$repo" "$dest"; then printf '%s' "$dest"; return 0; fi
  local dur=$((SECONDS - start)); rm -rf "$dest"

  # 网络层失败 → 切镜像；秒退失败 → 直接报错跳过
  if is_net_failure "$dur"; then
    printf '\033[33m    ⚠ github.com 无法触达（60s 内无数据），切换镜像源 %s\033[0m\n' "${MIRROR#https://}" >&2
    : > "$TMP_BASE/.use_mirror"   # 标记本次运行后续走镜像
    if clone_url "$MIRROR" "$repo" "$dest"; then printf '%s' "$dest"; return 0; fi
    rm -rf "$dest"; fail "镜像克隆失败: $repo"; return 1
  fi

  fail "克隆失败: $repo（耗时 ${dur}s）"; return 1
}

# 从 .your-skill-collection.json 读取条目列表（排除 skip，支持按名称过滤）
# 输出格式: name TAB repo TAB mode TAB payload
#   mode=subdir: payload=子目录路径（或空）
#   mode=files:  payload=JSON 数组字符串
read_skills() {
  python3 -c "
import json, os, sys
data = json.load(open(os.path.join(sys.argv[2], '.your-skill-collection.json')))
skips = set(data.get('skip', []))
f = set(sys.argv[1].split()) if sys.argv[1].strip() else None
for name, cfg in data['skills'].items():
    if name in skips:
        continue
    if f and name not in f:
        continue
    if 'files' in cfg:
        import json as j
        print(name + '\\t' + cfg['repo'] + '\\tfiles\\t' + j.dumps(cfg['files']))
    else:
        print(name + '\\t' + cfg['repo'] + '\\tsubdir\\t' + cfg.get('subdir', ''))
" "$FILTER" "$PYTHON_DIR"
}

[[ -n "$FILTER" ]] && log "更新 skills: $FILTER" || log "更新所有 skills"
echo

while IFS=$'\t' read -r name repo mode payload; do
  printf '  %s\n' "$name"
  dest="$SKILLS_DIR/$name"

  printf '    克隆 https://github.com/%s ... ' "$repo"
  repo_dir=$(get_clone "$repo") || continue

  # 备份旧版本到 .backup/<name>/（Claude Code 不会扫描隐藏目录）
  BACKUP_DIR="$SKILLS_DIR/.backup"
  mkdir -p "$BACKUP_DIR"
  if [[ -d "$dest" ]]; then
    rm -rf "$BACKUP_DIR/$name"
    cp -r "$dest" "$BACKUP_DIR/$name"
    rm -rf "$dest"
  fi
  mkdir -p "$dest"

  if [[ "$mode" == "files" ]]; then
    # 多源拼装模式：按文件列表逐一复制
    err=0
    while IFS=$'\t' read -r src_path dest_name; do
      full_src="$repo_dir/$src_path"
      full_dest="$dest/$dest_name"
      if [[ -f "$full_src" ]]; then
        cp "$full_src" "$full_dest" || { err=1; break; }
      elif [[ -d "$full_src" ]]; then
        cp -r "$full_src" "$full_dest" || { err=1; break; }
      else
        printf '\n'; fail "路径不存在: $src_path"; err=1; break
      fi
    done < <(python3 -c "
import json, sys
for item in json.loads(sys.argv[1]):
    print(item['src'] + '\\t' + item['dest'])
" "$payload")
    if [[ $err -eq 0 ]]; then ok; else
      fail "复制失败，恢复备份"
      rm -rf "$dest"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
    fi
  elif [[ -n "$payload" ]]; then
    src="$repo_dir/$payload"
    if [[ ! -d "$src" ]]; then
      fail "子目录不存在: $payload，恢复备份"
      rm -rf "$dest"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
      continue
    fi
    if cp -r "$src/".  "$dest/" 2>/dev/null || { rm -rf "$dest" && cp -r "$src" "$dest"; }; then ok; else
      fail "复制失败，恢复备份"
      rm -rf "$dest"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
    fi
  else
    if cp -r "$repo_dir/". "$dest/" && rm -rf "$dest/.git"; then ok; else
      fail "复制失败，恢复备份"
      rm -rf "$dest"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
    fi
  fi

done < <(read_skills)

echo
log "完成！如需回滚某个 skill: rm -rf <skill> && cp -r .backup/<skill> <skill>"
echo

# 如果在 git 仓库中，显示变更提示
if git -C "$SKILLS_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  changed=$(git -C "$SKILLS_DIR" status --short | grep -v '^\?\? \.backup/' | grep -v '^\?\? 说明' || true)
  if [[ -n "$changed" ]]; then
    printf '\033[33m─────────────────────────────────────────\033[0m\n'
    printf '\033[33m  有变更尚未提交到 GitHub：\033[0m\n'
    printf '%s\n' "$changed" | sed 's/^/    /'
    printf '\033[33m─────────────────────────────────────────\033[0m\n'
    printf '  git -C "%s" add -A && git -C "%s" commit -m "update skills" && git -C "%s" push\n' \
      "$SKILLS_DIR" "$SKILLS_DIR" "$SKILLS_DIR"
  else
    printf '  已是最新，无需提交。\n'
  fi
fi
