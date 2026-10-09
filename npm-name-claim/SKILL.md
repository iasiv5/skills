---
name: npm-name-claim
description: 抢注/占位发布 npm 包名：查名、搭 0.0.1 占位包、认证与发布的全流程，以及发布后配置 GitHub Actions OIDC Trusted Publishing（无 token 发版）。当用户想查 npm 包名是否被注册、想抢注/占位/保留（claim/reserve）npm package name、想把 npm 包升级为 OIDC/trusted publishing 发布、或 npm publish / npm trust 遇到认证与环境故障（E401、PUT 报 404、ENEEDAUTH、EOTP/2FA、静默失败 exit 1、镜像源发不出包）时使用。
---

# npm 包名抢注（占位发布）

npm 没有预留/停放机制：**名字只有在第一次成功 publish 之后才真正归属**。查完是空的就别拖，尽快发 0.0.1 占位版。

流程五步：**查名 → 搭包 → 认证 → 发布 → 验证**，外加卫生收尾。机械步骤由 `scripts/claim.sh` 承载（子命令用法看脚本内 USAGE），本文件只写决策点、交互协议和坑的原理。

## 快速开始

用户报来一个或多个包名时，按序调用：

```bash
scripts/claim.sh check <name> [<name>...]     # 多名批量逐行输出；单名附近似名
scripts/claim.sh scaffold <name> --dir BASE --desc ... --repo ... --homepage ... --author ...
scripts/claim.sh weblogin <pkgdir>            # 已有可用 token 时跳过
scripts/claim.sh publish <pkgdir>             # 用后台任务方式运行，见第 4 步
scripts/claim.sh verify <name> [--wait 180]
scripts/claim.sh cleanup <pkgdir>             # 全部发完后做
scripts/claim.sh trust <pkgdir> --repo OWNER/REPO --file <wf.yml>   # 可选：发包后配 OIDC 信任，见第 7 节
```

## 1. 查名

`claim.sh check` 返回 AVAILABLE / TAKEN（不合规或 registry 异常为 INVALID / UNKNOWN）；单名附近似名搜索，多名批量时逐行输出、省略近似名。

- 完成标准：向用户逐名明确「可抢 / 已占」。
- **AVAILABLE 只保证「未注册」**：npm 在 publish 时还有一层 typosquat 相似度拦截（详见第 4 步症状表），短名（≤4 字母）和常见词即使未注册也可能被拒。对短名要有此预期，先给用户打预防针。
- **发布前做「拼接心算」**：把全名连读一遍，读起来像现有单词就是高危名。实战教训（2026-10-09）：`dsh-ip` 连读成 **dship**、`dsh-op` 连读成 **dshop**，check 均 AVAILABLE，publish 全部 403 永久关闭。`dsh-` + 2 字母后缀是重灾区。
- 近似名一眼扫过即可：占自己的品牌名属于正常占位；蹭知名项目的近似名属于 typosquat，会被 npm 处理，拒绝协助。
- 提醒用户抓紧：查完到 publish 之间随时可能被人截胡。

## 2. 搭占位包

`claim.sh scaffold` 生成三件套（package.json / index.js / README.md）并自动做打包自检。

- `--desc` 与 keywords 按用户项目主题写正常文案——占位包也是公开门面。
- package.json 里已写死 `publishConfig.registry: https://registry.npmjs.org/`。这是防翻车关键：很多机器默认源是镜像（腾讯/淘宝等），镜像只能装、发不了，发布必须显式指回官方源。
- 完成标准：scaffold 输出「打包自检通过」。

## 3. 认证

token 的落点只有一个：`<pkgdir>/.npmrc`（chmod 600）。输出与聊天里只出现 token 长度；一旦出现明文，立即让用户去 npmjs.com 吊销该 token。

优先级从高到低：

1. **weblogin（推荐，零 token 暴露）**：`claim.sh weblogin <pkgdir>` 向 registry 发起 web 登录会话，输出 `LOGIN_URL:` 交给用户在浏览器打开并授权（有 2FA 就地完成），脚本轮询 doneUrl 拿到 token 后直写文件。
2. **用户自备 token**：让用户在 npmjs.com 生成 Access Token（Automation 类型），并**在用户自己的终端**里执行 `npm config set '//registry.npmjs.org/:_authToken' <token>`——token 经用户的手直达 `~/.npmrc`，绕开对话。
3. **存量 token**：`~/.npmrc` 里可能已有 token。判定失效看**失效签名**：`whoami` 返回 401 且 publish 的 PUT 返回 404（registry 对无效 token 的写操作掩饰成 404）。命中签名就重走 weblogin，与网络和包名无关。

`~/.npmrc` 本身可能位于只读挂载（沙箱/容器），所以 token 落点选包目录 `.npmrc`——npm 会加载包目录级配置。

完成标准：报出账号名，例如：

```bash
cd <pkgdir> && npm whoami --registry https://registry.npmjs.org --cache ../.npm-cache --logs-dir ../.npm-logs --userconfig .npmrc
```

注意：`~/.npm` 只读时 whoami 会报 `EROFS: read-only file system`——那是缓存目录崩溃，**不是认证失败**，把 `--cache`/`--logs-dir` 指到可写目录即可（同 publish 的坑，症状不同）。

## 4. 发布（含 2FA/EOTP 处理）

先对症，再动手：

| 症状 | 根因 | 解法 |
|---|---|---|
| `npm publish` / `npm pack` **静默 exit 1，无任何错误文本** | cache/logs 目录只读（如 `~/.npm` 在只读挂载），npm 内部崩溃并吞掉报错 | `--cache`、`--logs-dir` 指到可写目录（claim.sh 已内置，落在包目录父目录下） |
| PUT 404 + whoami 401（命中失效签名） | token 失效 | 重走第 3 步 |
| `EOTP: This operation requires a one-time password` | 账号 2FA 设为 auth-and-writes，写操作要二次验证 | 见下 |
| `npm trust` 任意子命令（**连 `list` 读操作**）报 `EOTP`，错误通道里授权链接是打码的 `***` | trust 属账号级敏感操作，auth-and-writes 账号一律二次验证，且 npm 把它走错误通道输出 | 与 publish 同一套伪 TTY + `--browser=false`（`claim.sh trust` 已内置）；`--browser` 这个 flag 传不进去就改用环境变量 `npm_config_browser=false` |
| `npm trust ... --cache/--logs-dir <dir>` 报 `Unknown positional argument: <dir>` | `npm trust` 的子命令用严格 flag 解析器，不认这些全局 flag 的空格分隔形式，值被当成了多余位置参数 | 相关配置全部改走 `npm_config_*` 环境变量（`npm_config_cache` / `npm_config_logs_dir` / `npm_config_browser`） |
| PUT `403 Package name too similar to existing packages ...` | npm typosquat 防护在发布时做相似度拦截（check 阶段看不到） | 该名对所有账号永久关闭，重试无意义；向用户说明并给替代：`@scope/name`（属自己账号，无抢注意义）或换名。实战例：dsh-ip≈dship、dsh-op≈dshop |

**EOTP 核心技巧：伪造 TTY + 关闭浏览器。** 具体命令在 `claim.sh` 的 publish 子命令里（`script -qec` 包一层伪终端，npm 加 `--browser=false`），这里写清楚它为什么有效——排障时据此推理：

- 非 TTY 环境下，npm 收到 EOTP 直接抛错退出；伪 TTY 让它改走 web-OTP 流程：打开 authUrl、轮询 doneUrl、拿到 OTP 票据后**自动重试发布**，全程无需手动输验证码。
- `--browser=false` 让 opener 把真实授权链接打印到输出后立即返回——npm 打印 URL 的通道关闭了脱敏（错误通道里的 URL 是打码的 `***`），并且弹浏览器、等回车两个动作都被跳过，适合 headless 环境。

交互协议：

1. **以后台任务运行** `claim.sh publish`（bash 工具 `run_in_background: true`）——它会阻塞等待用户授权。
2. 轮询任务输出，出现 `AUTH_URL: https://www.npmjs.com/auth/cli/...` 后立刻把链接发给用户，让用户完成登录 + 2FA + Authorize。
3. 用户授权后 npm 自动继续，任务输出出现 `PUBLISHED:` 即完成。
4. 链接过期或超时就重新运行一次，会生成新会话。

省事技巧：授权后有**宽限窗口**，短时间内同账号再发布其他包可复用授权、免二次 OTP。要抢多个包名时，把所有 scaffold 提前做好，认证+发布集中连着做，通常用户只点一次授权。

**批量连发配方**（实测：28 包一次授权、约 2 分钟发完 26 个）：

1. weblogin 一次拿 token，`cp <pkgdir>/.npmrc <其他包目录>/.npmrc && chmod 600 <其他包目录>/.npmrc` 全批共用；
2. 一个后台任务里顺序 publish 全部包，输出**流式透传**（宽限窗口内后续包免 OTP 自动过）：

```bash
for n in a b c; do
  echo "=== PUBLISH dsh-$n start $(date +%T) ==="
  bash scripts/claim.sh publish "/path/npm-packages/dsh-$n" 2>&1 \
    | grep --line-buffered -E "PUBLISHED|AUTH_URL|https://www\.npmjs\.com/auth|npm error"
  echo "=== dsh-$n exit=${PIPESTATUS[0]} $(date +%T) ==="
done
```

三个管道坑（2026-10-09 全踩过，任中一个都会让授权链接不可见、整批假死）：

- publish 输出**不要吞进变量**再判断——AUTH_URL 出现时 npm 正阻塞等用户授权，吞掉输出 = 死等且链接不可见；
- grep 必须加 `--line-buffered`：非 TTY 下 grep 块缓冲，已匹配的链接行会憋到进程退出才吐；
- 匹配模式必须包含裸 URL（`https://www\.npmjs\.com/auth`）——授权链接独立成行，只匹配 `AUTH_URL`/`Authenticate` 关键词会漏掉它。

完成标准：输出 `PUBLISHED:`。

## 5. 验证

`claim.sh verify <name>`：registry 返回 200 + 最新版本 + 发布者账号。把 `https://www.npmjs.com/package/<name>` 链接给用户，并告知：名字已锁定，以后发正式版就是改版本号后 `npm publish`。

**`0.0.0-stage` 与分钟级延迟是正常现象，不要重发**：全新包名首发成功后，registry 会先挂一条 `0.0.0-stage`（"Temporary package placeholder for staged publishing"）占位记录，真实版本约 1–2 分钟后才转正为 latest；期间 verify 可能显示 `LIVE: name@0.0.0-stage`，甚至在前几十秒短暂 404。publish 已受理，此时重发只会徒增失败。需要确认转正就用 `claim.sh verify <name> --wait 180` 轮询，输出 `STAGED:` 表示仍在转正中。

完成标准：verify 输出 `LIVE:`（版本号为真实版本而非 `0.0.0-stage`）。

## 6. 卫生收尾

- `claim.sh cleanup <pkgdir>` 删除包目录里的 token 文件。占位包发布完成后建议清掉；下次发版重走 weblogin（用户点一次链接的事）。
- 完成标准：各包目录里已无 `.npmrc`。

## 7. Trusted Publishing（GitHub Actions OIDC，无 token 发版）

占位包发完后，可顺手把包升级成 OIDC 信任发布：以后发版不再需要任何静态
token，CI 用短时凭据且自带 provenance。

1. **前提：包必须已存在**——首发无法直接 OIDC（npm/cli#8544 仍 open）。
   第 2 步的 0.0.1 bootstrap 正好铺平这条路，这是「先 bootstrap 再 OIDC」
   发布策略的根因，不只是抢名；
2. **配置信任**：`claim.sh trust <pkgdir> --repo OWNER/REPO --file <workflow.yml>`
   （内部 `npm trust github`，需要 npm ≥ 11.10；workflow 只写文件名不带
   路径）。等价于 npmjs.com 网站上的 Trusted Publisher 表单，但全程 CLI +
   一次浏览器授权，无需登录网站；
3. **仓库里放 workflow**，三要素：`permissions: id-token: write`；npm ≥
   11.5.1（setup-node 装 node 24，`npm install -g npm@latest` 兜底）；
   `npm publish --provenance --access public`。触发用 `on: push: tags: ['v*']`，
   另加 `workflow_dispatch` 方便重跑；
4. **发版 = 打 tag**：`npm version x.y.z && git push --tags`，Actions 自动
   发布。registry 元数据里发布者显示为 `GitHub Actions` 即 OIDC 生效
   （`claim.sh verify` 会直接把它打出来）。

实战样例（2026-09-18）：`@iasiv5/dsh-obmc-web`，0.0.1 bootstrap → weblogin
→ `trust` 配信任 → cleanup 删 token → 推 `v0.1.0` tag → Actions 发布。

## 依赖与移植

bash、curl、node、npm、util-linux 的 `script`；`trust` 子命令额外要求
npm ≥ 11.10。换机器/新环境使用：整个 skill 目录拷贝到该环境的 skill 目录
即可，脚本无其他依赖。
