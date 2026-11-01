# @iasiv5/dsh-skills DSH 插件化分发 实施计划

> 修订 A（2026-11-01 评审 R1）：skill 计数 27→28（评审 Q1）；invocation 按 frontmatter 透传 + DoD 精确集合 22+6（Q2）；Task 8 白名单 29 项 + `.git` 排除（Q3）；NOTICE 覆盖扩至 20 个上游来源、素材源改仓库（Q4/Q8）；锁文件提交 + `npm ci`（Q5/Q7）；重启生效判据可观测化（Q6）；版本门禁首发特判（Q9）；判据命令退出码卫生（Q10）。
> 修订 B（2026-11-01 评审 R2）：Task 9 补 dsh-m 发版链（push ≠ 市场可见，Q13）；Task 8 Step 3 改全集逐项断言堵假绿通道（Q14）；重启探针加轮询 ≤120s 防启动竞态（Q15）；ADR 0002 勘误 28、核查落盘直路径、Task 6 加 git 干净前置（Q16）。
> 定稿（2026-11-01）：评审通过（16 项闭环）；D1 计数勘误 28、D2 NOTICE 扩至 20 上游、D3 id `dsh-skills` 均经主人批示，待决策标注已清除。
> 执行勘误 C（2026-11-01）：门禁③语义细化——「打包分歧」（引用目标在仓库内存在但在打包目录集之外）为 fail；「既有悬空引用」（源中即缺失，上游原样）与文档写法示例降为 warn 非阻断（as-is 照带，构建报告如实计数）；提取器过滤 `<占位符>`/`file:`/绝对路径/glob。
> 执行勘误 D（2026-11-01，主人批示 D4/D5）：**剔除 4 个 skill 出包**——docx/pdf/xlsx（Anthropic LICENSE 禁第三方再分发，Task 4 Step 2 审计实锤）+ remotion-best-practices（上游 404 无许可）；仓库原样保留，构建脚本 `PACKAGING_EXCLUDE` 显式排除。**打包集 28 → 24（18 model-invocable + 6 斜杠）**；ADR 0003 已补修订节；NOTICE 改「收录 24 + 未收录 4 及缘由」双层结构（原「恰 20 条」分节断言随落地形态改为覆盖性断言）；Geek ×2 修正为 staruhub/ClaudeSkills 仓库级 MIT；附带修正：`dsh-plugin/node_modules` 误跟踪已移出索引并入 gitignore，门禁④加 pack 禁入路径硬断言（fail-closed）。Task 8 迁移白名单改 **25 项**（24 skill + `docs`）——4 个剔除 skill 的本地副本**保留**（插件不提供它们，本地保留即保持可用，且不涉 npm 再分发）。
> 执行勘误 E（2026-11-01 13:48，**主人手动执行**）：`~/.agents/skills` 整目录由主人删除（超 Task 8 计划范围：含 lark-*×28、4 个剔除 skill 本地副本、6 个斜杠 skill 本地副本、`.git` 工作树与文件级残留；**无备份**）。Task 8 全部 Step 作废留档，验收缩为：新会话 18 项 ✓（执行会话重启后 catalog 已实测 18/18 逐名吻合，Task 5 Step 4 证据注记）、4 剔除项不再出现 ✓、6 斜杠走插件（`/eli5` 可随时冒烟）。**lark-*×28 本机退役**，回迁与否待主人后续指示（可从 Host B 或 lark-cli 同步源找回）。`~/.agents/skills` 遮蔽问题随之消灭，B7 目标以更强形态达成。
> 执行勘误 F（2026-11-01，主人批示 B + 增补）：①装机形态定稿 **B（全走发版）**——本机 npm 源，不回切 link:（已记入 Task 7 Produces）；②update.sh 末尾增补 **DSH staging 自动重建委派**（能力检测：`dsh-plugin/node_modules` 就绪才跑 `npm run build`，未就绪提示跳过；构建失败独立 exit 1 不污染「内容已同步」语义）——update.sh→build 焊成一键；③`dsh-plugin/node_modules` git 历史已 filter-branch 抹除（改写后哈希：8a817a9→40856c3 等，均未推送）+ gitignore `node_modules/`；④icon 两版迭代定稿家族公式（36 透明 viewBox、b/t 标准渐变、三卡叠放+星芒镂空）；⑤ci.yml 摘除恒真 `--check` 步骤（CI 内 staging 与比对同源）。

## 目标

把本仓 28 个 skill 中的 **24 个**（勘误 D：docx/pdf/xlsx/remotion-best-practices 因许可剔除出包，仓库保留）以**单包全量**方式改造为 DSH 插件 `@iasiv5/dsh-skills`：仓库内新增 `dsh-plugin/` wrapper，构建期同步 skills、发版到 npm，web 机装机并通过 DoD 验收，随后清理本机 `~/.agents/skills/` 旧副本、收录 dsh-m（audience internal），并产出 desktop 机跟进清单。

## 架构快照

- DSH 宿主的 skill 注册表（`ctx.skills`）支持插件经 `ctx.skills.registerProvider()` 注册 bundled skill（rank 600，优先级最低）。插件为**纯 host 插件**：无 client bundle、无路由、无 locale，参照 JimLiu/baoyu-design 的 `dsh-plugins/dsh-claude-slides` 三件套（package.json / cordis.patch.yml / lib/index.js）。
- 根目录各 skill 目录（`answer-me-with-html/` … `xlsx/`，2026-11-01 实测 28 个，含 `Geek-skills-*` 前缀目录）是**唯一编辑源**；`dsh-plugin/skills/` 为构建期临时副本（gitignore）。构建脚本同时生成 `dsh-plugin/skills-manifest.json`（frontmatter 预解析结果，含 invocation 预计算），运行时 provider 零依赖读 manifest。
- 发布走 GitHub Actions tag → OIDC Trusted Publishing（dsh-surf/dsh-skins 同款）；装机与迁移在 web 机（`deepseek-harness.service`，profile `web`）执行。

## 全局约束（逐字继承自共识与 ADR 0002/0003）

- npm 包名 `@iasiv5/dsh-skills`；cordis.patch.yml 插行 `id: iasi-skills`、`name: "@iasiv5/dsh-skills"`；provider 名 = npm 包名。
- `engines`: `{"node": ">=20", "dsh": ">=0.2.0-0"}`；`dsh.bundle.patch: "./cordis.patch.yml"`。
- **零 runtime 依赖**；禁止任何 `@deepseek-ai/*` 依赖（know-how 041）；devDependencies 仅 `yaml`（构建/测试期用），`package-lock.json` 随仓提交，CI 用 `npm ci`。
- **as-is 不裁剪**（ADR 0003）：skill 目录内文件原样进包；LICENSE 保留；根级 `NOTICE.md` 汇总归属。
- bundled skill rank = 600（`BUNDLED_SKILL_RANK`）。**invocation 按 frontmatter 透传**（与宿主 `parseInvocationPolicy` 同语义）：`disable-model-invocation: true` → `modelInvocable: false`；`user-invocable: false` → `userInvocable: false`；缺省两值均为 true；legacy 键（`disableModelInvocation`/`modelInvocable`/`userInvocable`）非法，构建门禁拒绝。frontmatter 有 `whenToUse` 则透传。
- **计数基线（2026-11-01 实测，勘误 D 后）**：仓库 28 个 skill；**打包 24 个 = 18 个 model-invocable + 6 个 `disable-model-invocation`**（cleanup、eli5、grill-with-docs、improve-codebase-architecture、retro、teach）；`PACKAGING_EXCLUDE` = docx/pdf/xlsx/remotion-best-practices（许可剔除，勘误 D）。构建输出动态计数 `N skills staged` 并断言 N == manifest 条数；判据引用名单处均以此二清单为准，防仓库演化后数字漂移。
- 版本语义：新增 skill = minor，内容修订 = patch，移除/更名 = major（CI 门禁强制）；首发 **1.0.0**。
- dsh-m 条目：id `dsh-skills`、category `self-dev`、`audience: "internal"`、`decoupled: true`、verified `["0.2.1-rc.5"]`。（id 已经主人批示 D3 定稿：现役 6 条自研条目全为 npm 短名，基线 B11 原文 `iasiv5__skills` 系与 awesome-dsh 社区目录惯例混淆，按 registry 实况取短名。）
- web 机环境红线：npm 一律 `export npm_config_cache=~/workspace/.npm-ci-cache`；npm 轮询加 `--registry=https://registry.npmjs.org`（know-how 035⑥）；profiles 禁裸写，装/卸走 `dsh plugin --profile web …` 通道（know-how 026）；**重启一律 `dshm_restart`，禁在当轮 inline `systemctl restart`**（know-how 037）。
- **`dshm_restart` 是 agent 工具调用（宿主通道），不是 dsh CLI 子命令**——本计划 Run: 字段中出现它时，指「调用 dshm_restart 工具」，不得敲进 bash；重启生效判据一律用 `systemctl show deepseek-harness.service -P ActiveEnterTimestamp` 时间戳推进（工具返回成功 ≠ 重启已发生）。

## 输入工件

- 设计共识：`docs/adr/0002-plugin-distribution-as-dsh-bundle.md`、`docs/adr/0003-third-party-skills-as-is-with-notice.md`、根 `GLOSSARY.md`（插件分发术语 4 条）
- 参照实现：`~/workspace/.dsh-research/dsh-claude-slides-index.js`（baoyu dsh-claude-slides 完整入口源码）
- 宿主事实：`dsh-skill-filesystem` rank 表（project-dsh 100 / project-agents 200 / custom 300 / user-dsh 400 / user-agents 500 / bundled 600）；skill 发现以 frontmatter `name:` 为准；invocation 键语义 = `parseInvocationPolicy`（`disable-model-invocation` / `user-invocable`，legacy 键抛错）
- 上游来源真源：`.your-skill-collection.json` skills 表（21 条记录；其中 `Geek-skills-wechat-article-writer` 表内有记录但未收录本仓，NOTICE 不含它）
- 发版 SOP：npm-name-claim skill（OIDC Trusted Publishing 配置）、know-how 018（staged 发布轮询）、dsh-skins `release.yml` 先例

## 文件结构与职责

- Create: `dsh-plugin/package.json` — 插件包清单（唯一 npm 发布入口）
- Create: `dsh-plugin/package-lock.json` — 锁 devDependencies（Task 3 Step 1 生成并提交；release.yml `npm ci` 的前提）
- Create: `dsh-plugin/lib/index.js` — cordis 插件入口：`inject: ["skills"]`，`apply()` 注册 provider
- Create: `dsh-plugin/cordis.patch.yml` — 往 profile bundle 插一行插件挂载
- Create: `dsh-plugin/icon.svg` — 市场卡片图标（占位设计，主人可替换）
- Create: `dsh-plugin/NOTICE.md` — 第三方归属汇总（ADR 0003；覆盖全部 20 个上游来源）
- Create: `dsh-plugin/README.md` — 插件包自述（安装方式、skill 清单指向）
- Create: `dsh-plugin/skills-manifest.json` — 构建产物（gitignore），schema 见 Task 2 接口契约
- Create: `dsh-plugin/skills/` — 构建产物（gitignore），24 个收录 skill 目录的同步副本（勘误 D：4 个许可剔除目录不入）
- Create: `dsh-plugin/scripts/build.mjs` — 同步 + manifest 生成 + 门禁 + 体积报告
- Create: `dsh-plugin/test/provider.test.mjs` — `node --test` 单测（fixture 驱动）
- Create: `.github/workflows/release.yml` — tag 触发构建 + 版本门禁 + OIDC 发布
- Create: `.github/workflows/ci.yml` — push/pr 跑 build 门禁 + 单测
- Create: `README.md`（仓库根，现无）— 面向访客的总述 + DSH 插件安装节
- Modify: `.gitignore` — 追加 `dsh-plugin/skills/`、`dsh-plugin/skills-manifest.json`
- Modify: `update.sh` — 头部注释加「DSH 用户走插件安装，本脚本不再适用于 DSH」
- Modify: `dsh-m/registry.json`（另一仓库 `~/workspace/dsh-m`）— Task 9 收录

## 任务清单

### Task 1: 风险探针——最小空插件验证装载路径

- 目标：证明「纯 host、无 client、无路由」插件能被 0.2.1-rc.5 装载器激活（此前无先例，先排雷再灌内容）。
- 涉及文件：Create `dsh-plugin/package.json`、`dsh-plugin/cordis.patch.yml`、`dsh-plugin/lib/index.js`（探针版：provider 返回空列表）、`dsh-plugin/icon.svg`。
- 接口契约
  - Consumes: 无
  - Produces: 三件套文件骨架；`package.json` 字段集（后续任务只增不改）：`name=@iasiv5/dsh-skills`、`version=1.0.0`、`type=module`、`main=lib/index.js`、`files=["lib","skills","cordis.patch.yml","icon.svg","NOTICE.md","README.md","skills-manifest.json"]`、`engines`、`dsh.bundle.patch`；`lib/index.js` 导出 `{ name: "iasi-skills", apply }`，`apply(ctx)` 内 `ctx.skills.registerProvider(() => provider)`，provider 形如 `{ name: "@iasiv5/dsh-skills", list: async () => candidates, get: async (candidate) => ({...candidate 摘要, content}) }`；**重启生效探针范式**（Task 5/7/8 复用）：重启前记录 `systemctl show deepseek-harness.service -P ActiveEnterTimestamp`（T0）→ `dshm_restart` 工具 → **轮询再读（每 ~5s，上限 120s）直至 T1 > T0**（工具返回时服务可能仍在启动，单次读取会遇旧值假失败），配合 journal 锚点构成联合判据
- 验证范围：journal 激活锚点干净 + 重启时间戳推进 + 卸载后 profile 无本包。

- [ ] Step 1: 写探针三件套（package.json 按上述字段集、cordis.patch.yml 一行 insert、index.js 空 provider、icon.svg 占位图形）
- [ ] Step 2: 本机 folder 安装（不发布、不走 npm）
- Run: `dsh plugin --profile web add /home/ubuntu/workspace/skills/dsh-plugin`
- Expected: 命令退出码 0，输出含 installed/added
- [ ] Step 3: 重启加载（生效判据 = 时间戳推进，非工具返回）
- Run: `systemctl show deepseek-harness.service -P ActiveEnterTimestamp`（记 T0）→ 调用 `dshm_restart` 工具 → 轮询 `systemctl show deepseek-harness.service -P ActiveEnterTimestamp`（每 ~5s，上限 120s）
- Expected: 轮询窗口内 T1 > T0（重启真实发生）；工具返回成功仅为前置，不作生效判据；120s 仍 T1 == T0 = 失败，按 know-how 037 排查
- [ ] Step 4: journal 激活锚点检查（与 Step 3 构成联合判据）
- Run: `sudo journalctl -u deepseek-harness.service --since "-10 min" | grep -E "did not activate|skipping profile bundle|iasi-skills|dsh-skills" || true`
- Expected: 无 `did not activate`、无 `skipping profile bundle`；如出现 `iasi-skills`/`dsh-skills` 相关行应为激活/加载类而非报错
- [ ] Step 5: 健康检查（辅助信号，不作生效判据）
- Run: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3080`
- Expected: `200`
- [ ] Step 6: 卸载探针
- Run: `dsh plugin --profile web remove @iasiv5/dsh-skills`（`dsh plugin` 实为向 profile 目录内 pnpm 转发，子命令以 `dsh plugin --help` 实测为准）→ `dshm_restart` 工具 → 同 Step 3/4 时间戳 + journal 探针
- Expected: 时间戳推进；`dsh plugin --profile web list` 输出无 `@iasiv5/dsh-skills`；journal 无报错

### Task 2: provider 完整实现 + manifest schema（fixture 单测）

- 目标：`lib/index.js` 完整实现「读 manifest → 注册候选 → 按需读 SKILL.md 正文」，用 fixture 数据在无宿主环境下单测。
- 涉及文件：Modify `dsh-plugin/lib/index.js`；Create `dsh-plugin/test/provider.test.mjs`。
- 接口契约
  - Consumes: Task 1 的导出骨架
  - Produces: **`skills-manifest.json` schema**（后续 Task 3 按此生成）：`{ "skills": [ { "dir": "<skills/ 下目录名>", "name": "<frontmatter name>", "description": "<frontmatter description>", "whenToUse": "<有则字符串>", "invocation": { "modelInvocable": <bool>, "userInvocable": <bool> } } ] }`——`invocation` 由 build 按 frontmatter `disable-model-invocation`/`user-invocable` 以宿主 `parseInvocationPolicy` 同语义**预计算**（缺省均 true）；实现行为：`apply(ctx, config = {})` 读 manifest（路径 = `config.manifestDir ?? packageRoot` 下的 `skills-manifest.json`，`manifestDir` 供单测注入 fixture 目录；生产路径即 packageRoot），对每条生成 candidate `{ name, description, ...(whenToUse ? { whenToUse } : {}), invocation: <manifest 条目原样透传>, provider: "@iasiv5/dsh-skills", source: "bundled", rank: 600, path: join(base,"skills",dir,"SKILL.md"), resourceBase: { kind: "directory", path: join(base,"skills",dir) }，其中 base = `config.manifestDir ?? packageRoot`（执行勘误 2026-11-01：candidate 路径基座须与 manifest 同源，否则 fixture 注入下 `get()` 读不到 SKILL.md） }`（路径统一 POSIX 分隔符）；`get()` 读 `path`、剥离 YAML frontmatter、返回 `{ name, description, invocation, provider, source, resourceBase, path, content }`
- 验证范围：`node --test dsh-plugin/test/provider.test.mjs` 全绿（含 invocation 透传断言）。

- [ ] Step 1: 写失败单测：fixture 目录 `test/fixtures/`（含 `skills-manifest.json` + `skills/demo-skill/SKILL.md`（默认 invocation）+ `skills/demo-slash-only/SKILL.md`（manifest 标 `modelInvocable:false`）），以 `apply(fakeCtx, { manifestDir: fixtureDir })` 注入，断言：list() 返回 2 条 candidate 且字段齐、`demo-slash-only` 的 `invocation.modelInvocable === false` 透传不失真、get() 返回正文含 fixture 正文标记、缺 manifest 时 apply 抛错
- Run: `node --test dsh-plugin/test/provider.test.mjs`
- Expected: 失败（实现未完成/断言不满足）
- [ ] Step 2: 实现 provider（manifest 读取、candidates 构建、get 正文剥离），frontmatter 剥离用 `^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)` 正则（baoyu 同款）
- [ ] Step 3: 跑单测
- Run: `node --test dsh-plugin/test/provider.test.mjs`
- Expected: 全部 pass，0 fail
- [ ] Step 4: checkpoint commit（`feat(dsh-plugin): provider implementation with manifest schema`）

### Task 3: 构建脚本 + 门禁（stage、manifest、校验、体积报告）

- 目标：一条命令完成「根 skill 目录 → dsh-plugin/skills/ 同步 + 生成 manifest + 四项门禁 + npm pack 体积报告」。
- 涉及文件：Create `dsh-plugin/scripts/build.mjs`、`dsh-plugin/package-lock.json`（本任务生成）；Modify `package.json`（加 `"scripts": {"build": "node scripts/build.mjs", "test": "node --test test/provider.test.mjs"}`）；Modify 根 `.gitignore`（追加 `dsh-plugin/skills/`、`dsh-plugin/skills-manifest.json`）。
- 接口契约
  - Consumes: Task 2 的 manifest schema；根目录 skill 目录（以「根目录下含 `SKILL.md` 的目录」**动态发现**，硬编码名单禁用；`.backup/`（gitignore）无根级 SKILL.md，天然不在集合内）
  - Produces: `dsh-plugin/skills-manifest.json`（真实 24 条）、`dsh-plugin/skills/<目录>` 副本、`dsh-plugin/package-lock.json`（提交入库）；门禁命令 `node dsh-plugin/scripts/build.mjs --check`（CI 用，只校验不同步）；退出码约定 0=过 / 1=挂
- 门禁四项：① 每个目录 `SKILL.md` 存在且 frontmatter 可被 `yaml` 解析、含非空 `name`/`description`，且 invocation 键合法——`disable-model-invocation`/`user-invocable` 为可解析布尔（true/false/1/0/yes/no/on/off），legacy 键（`disableModelInvocation`/`modelInvocable`/`userInvocable`）拒绝（与宿主 `rejectLegacyInvocationKey` 同语义）；② 全仓 frontmatter `name` 全局唯一（`keqian-method` 等与目录名不同以 frontmatter 为准）；③ 引用完整性冒烟（执行勘误 C 两级语义）：扫每个 `SKILL.md` 中的相对路径引用（`](./…)`、`](…/)` 与反引号内 `scripts/…`、`assets/…`、`references/…`、`docs/…` 字面引用，过滤 `<占位符>`/`file:`/绝对路径/glob）；**fail = 打包分歧**（目标在仓库内存在但在打包目录集之外——老全仓布局可用、打包后必断）；**warn = 既有悬空**（源中即缺失，上游原样照带、构建报告计数）；④ `npm pack --dry-run` 成功并打印 tarball 体积
- 验证范围：build 全绿且 manifest 24 条；人为破坏用例转红。

- [ ] Step 1: 写 `scripts/build.mjs` 骨架（空 staging 逻辑 + 「0 个 skill 目录」守卫）、`package.json` scripts + devDependencies（`"yaml": "^2"`）、根 `.gitignore` 追加两条；**先 `npm install`（生成 `package-lock.json`）并提交锁文件**——依赖就位后 Step 2 的失败信号才是计数守卫而非 `Cannot find package 'yaml'`
- [ ] Step 2: 运行确认失败（骨架 staging 源为空）
- Run: `cd dsh-plugin && npm run build`
- Expected: 退出码 1，报错含 skill 目录计数为 0
- [ ] Step 3: 实现 staging/manifest/门禁全量逻辑（同步用 `fs.cp`；manifest 按 dir 字典序；invocation 预计算入 manifest；四项门禁；`npm pack --dry-run` 体积报告）
- [ ] Step 4: 全量构建通过
- Run: `cd dsh-plugin && npm run build`
- Expected: 退出码 0，输出 `24 skills staged`（动态计数 N，N == manifest.skills.length == 24；另打印 `excluded from package (license policy): docx, pdf, remotion-best-practices, xlsx`）、体积报告、四项门禁全过（含 pack 禁入路径硬断言）
- [ ] Step 5: 负向验证（防门禁空转）：临时把某个 SKILL.md 的 `name:` 改成与另一 skill 重复
- Run: `cd dsh-plugin && npm run build`
- Expected: 退出码 1，报「duplicate skill name」；还原后重跑恢复绿
- [ ] Step 6: 单测回归仍绿
- Run: `cd dsh-plugin && npm test`
- Expected: pass
- [ ] Step 7: checkpoint commit（`feat(dsh-plugin): build script with staging, manifest and gates`，含 package-lock.json）

### Task 4: 文档与物料（NOTICE、README、update.sh 注记）

- 目标：补齐发包必需物料与仓库门面文档。
- 涉及文件：Create `dsh-plugin/NOTICE.md`、`dsh-plugin/README.md`、根 `README.md`；Modify `update.sh`（头部注释）。
- 接口契约
  - Consumes: `.your-skill-collection.json` skills 表（上游真源；表内 `Geek-skills-wechat-article-writer` 未收录本仓，NOTICE 不含）；仓库实况 LICENSE 分布（7 有 / answer-me-with-html 仅 `licenses/` 素材许可 / 12 无）
  - Produces: `NOTICE.md` 结构（Task 9 的 dsh-m 描述文案引用它）：**覆盖全部 20 个在仓上游 skill**——7 个带包内 LICENSE（docx/pdf/xlsx/guizang-ppt-skill/guizang-social-card-skill/darwin-skill/note-slides）逐条记录许可证类型与版权行；answer-me-with-html 记 `licenses/`（OFL-Bangers.txt 等）+ 上游 repo；其余 12 个（architecture-diagram、remotion-best-practices、mattpocock 系 8 个、Geek ×2）如实标「包内未含许可文本 + 上游 repo 链接」，Geek ×2 上游本身亦未声明。根 README「DSH 插件安装」节（安装命令与 `dsh-m` 收录后的入口说明）
- 验证范围：NOTICE 恰 20 条上游记录、README 安装命令与全局约束一致、上游条款核查留痕。

- [ ] Step 1: 素材收集——**从仓库源 `~/workspace/skills/` 读取**（NOTICE 描述的是随包分发的仓库内容；勿读 `~/.agents/skills/` 安装副本，Task 8 之后该副本将不存在）
- Run: `head -3 ~/workspace/skills/{docx,pdf,xlsx,guizang-ppt-skill,guizang-social-card-skill,darwin-skill,note-slides}/LICENSE* ; ls ~/workspace/skills/answer-me-with-html/licenses/`
- Expected: 获得各许可证标识与素材许可清单（写入 NOTICE 的素材）
- [ ] Step 2: 上游条款核查（ADR 0003 的发版前义务）：对 20 个上游 repo 查 LICENSE（GitHub raw/API），重点筛查「禁止再分发」类条款；无 LICENSE 的如实记录（含 Geek ×2 上游 repo 亦未声明）；核查输出落盘 `~/workspace/.dsh-research/dsh-skills-plan-review/license-audit-2026-11.md`（私有 scratch；如主人要公开可后移仓库 docs/）
- [ ] Step 3: 写 `NOTICE.md`（20 条）、`dsh-plugin/README.md`、根 `README.md`、`update.sh` 注记
- [ ] Step 4: 核对（显式断言，不用 `grep -c` 进 `&&` 链）
- Run: `[ "$(grep -c '^## ' dsh-plugin/NOTICE.md)" = "20" ] && grep -n "dsh plugin --profile web add @iasiv5/dsh-skills" README.md`
- Expected: NOTICE 分节恰 20；README 含安装命令行（任一失败即退出码非 0）
- [ ] Step 5: checkpoint commit（`docs(dsh-plugin): notice, readme and update.sh deprecation note`）

### Task 5: 本地端到端（folder 安装全量 24 skill）

- 目标：发布前在 web 机用 folder 安装验证全量注册（复用 Task 1 已验证的装载路径，灌真内容）。
- 涉及文件：无新增（消费 Task 3 产物）。
- 接口契约
  - Consumes: Task 3 的 staged `dsh-plugin/skills/` + manifest；Task 1 的安装命令与重启生效探针范式（T0/T1 时间戳 + journal 联合判据）
  - Produces: 主人新会话 skill 清单核对（DoD 第③条的预演）
- 验证范围：journal 干净 + 时间戳推进 + 主人新会话 18 项 model 可见 + `/eli5` 冒烟。

- [ ] Step 1: 重新构建确保产物最新
- Run: `cd dsh-plugin && npm run build`
- Expected: 退出码 0，`24 skills staged`
- [ ] Step 2: folder 安装 + `dshm_restart` 工具（按 Task 1 Step 3 探针范式，轮询 ≤120s 至 T1 > T0）
- Run: `dsh plugin --profile web add /home/ubuntu/workspace/skills/dsh-plugin` → `dshm_restart` 工具
- Expected: 安装成功、轮询窗口内 T1 > T0
- [ ] Step 3: journal 锚点检查（同 Task 1 Step 4 命令）
- Expected: 无 `did not activate` / `skipping profile bundle`
- [ ] Step 4: 🔴 主人协同验证点——开一个**新会话**核对：**18 个 model-invocable skill 全部出现**在 available_skills（清单：answer-me-with-html, architecture-diagram, brainstorming, code-review, codebase-design, darwin-skill, domain-modeling, grilling, guizang-ppt-skill, guizang-social-card-skill, handoff, keqian-method, note-slides, npm-name-claim, wechat-draft, writing-for-agents, writing-plans, xuefeng-method）；**6 个 `disable-model-invocation` skill（cleanup, eli5, grill-with-docs, improve-codebase-architecture, retro, teach）不出现在 catalog 属预期**，经斜杠调用验证——当场 `/eli5` 冒烟一次；**docx/pdf/xlsx/remotion-best-practices 不在 catalog 属预期**（勘误 D 许可剔除；本地 `~/.agents/skills` 副本尚在时会以 rank 500 出现——Task 8 清理前的过渡期现状，如实记录即可）（注意：`Geek-skills-*` 目录名不出现，出现的是 `keqian-method`/`xuefeng-method`；非本仓 skill（lark-* 等）恒在场，不作判据）
- Expected: 18 项齐、`/eli5` 冒烟正常
- [ ] Step 5: 记录结果后暂不卸载（Task 7 直接换成正式源）

### Task 6: 发布流水线 + 首发 1.0.0

- 目标：tag 触发 OIDC 发布到 npm，版本语义门禁上 CI。
- 涉及文件：Create `.github/workflows/release.yml`、`.github/workflows/ci.yml`；Modify `package.json`（版本确认 1.0.0）。
- 接口契约
  - Consumes: Task 3 的 `build --check`、门禁命令与**已提交的 `package-lock.json`**；npm-name-claim skill 的 Trusted Publisher 配置 SOP（一次性，需主人在 npm 网站与 GitHub 仓库设置操作）；know-how 018 轮询纪律
  - Produces: npm 上 `@iasiv5/dsh-skills@1.0.0`；版本门禁规则（含首发特判）：`npm view @iasiv5/dsh-skills --json` 查上一版——**不存在（404）→ 放行，但断言 git tag == package.json version == 1.0.0**；存在 → 对比上一版包内 `skills-manifest.json` 的 name 集合，新增=minor、移除/更名=major、仅修订=patch，不符则 publish 步骤失败，且同样断言 tag == version
- 验证范围：npmjs registry 直查出现 1.0.0；tarball 内容审计通过。

- [ ] Step 1: 写 release.yml（job：checkout → setup-node 20 → `npm ci`（dsh-plugin 内，依赖已提交的 package-lock.json；本包仅 1 个 devDep，npm 链路与 `npm publish`/OIDC 一致，不引入 pnpm）→ `npm run build` → `npm test` → 版本门禁脚本（内联 node 脚本，npmjs 直查，含首发特判）→ `npm publish`（`cwd: dsh-plugin`，`--provenance`，`NPM_CONFIG_PROVENANCE: true`，OIDC `permissions: id-token: write`））与 ci.yml（push/pr：build + test）
- [ ] Step 2: tarball 预审计（本地等价发布物检查）
- Run: `cd dsh-plugin && npm pack --dry-run`
- Expected: files 列表含 `skills/` 下 24 目录、`lib/`、`skills-manifest.json`、`cordis.patch.yml`、`icon.svg`、`NOTICE.md`、`README.md`；不含 `node_modules`、`test/`、`scripts/`（门禁④硬断言兜底）
- [ ] Step 3: 🔴 主人协同点——按 npm-name-claim skill 完成 Trusted Publisher 配置（npm 网站 + GitHub Actions 权限）
- [ ] Step 4: 合入 main 并打标（工作在 main 前先经主人确认）。**前置检查：`git -C ~/workspace/skills status --porcelain` 为空**——本评审批次的文档产物（ADR 0002/0003、GLOSSARY 增补、本计划）必须先全部提交，否则 push main 不含它们
- Run: `git -C ~/workspace/skills status --porcelain`（应为空）→ `git push origin main && git tag v1.0.0 && git push origin v1.0.0`
- Expected: Actions release run 触发并绿
- [ ] Step 5: registry 转正轮询（know-how 018：绿 ≠ 已上架，npmjs 直查）
- Run: `export npm_config_cache=~/workspace/.npm-ci-cache; npm view @iasiv5/dsh-skills@1.0.0 version --registry=https://registry.npmjs.org`
- Expected: 返回 `1.0.0`（分钟级 processing，等待窗口内不重推 tag）
- [ ] Step 6: checkpoint commit（workflow 文件合入即已提交；此处确认 run 日志归档）

### Task 7: web 机正式装机 + DoD 验收

- 目标：从 npm 正式源安装，跑完整 DoD。
- 涉及文件：无新增。
- 接口契约
  - Consumes: Task 6 的 npm 1.0.0；Task 5 已在装 folder 版（先卸载防双装）；Task 1 重启生效探针范式
  - Produces: 装机事实（Task 9 的 verified 与 dsh-m 描述引用）；**装机形态定稿（主人批示 B，2026-11-01）：本机同样保持 npm 源，接受发版驱动更新，不回切 link: 安装**——此后本机跟进上游变化的路径 = update.sh → `npm run build`（门禁）→ commit/push/tag → CI 发布 → `dshm_upgrade`
- 验证范围：DoD 全过。

- [ ] Step 1: 卸载 folder 版
- Run: `dsh plugin --profile web remove @iasiv5/dsh-skills`
- Expected: 移除成功；`dsh plugin --profile web list` 输出无本包
- [ ] Step 2: npm 正式安装
- Run: `dsh plugin --profile web add @iasiv5/dsh-skills`
- Expected: 安装成功（若遇 `minimumReleaseAge` 类拦截，按 know-how 020 包名级豁免或等 24h 窗口）
- [ ] Step 3: `dshm_restart` 工具 → T0/T1 时间戳推进（轮询 ≤120s，同 Task 1 Step 3）+ journal 锚点检查（联合判据）；HTTP 200 仅辅助
- [ ] Step 4: 🔴 主人协同验证点——新会话 18 项 model 可见 + `/eli5` 冒烟（同 Task 5 Step 4 双清单）
- [ ] Step 5: 记录装机事实：`~/.dsh/profiles/web/node_modules/@iasiv5/dsh-skills/package.json` 的 version 应为 1.0.0
- Run: `node -p "require('/home/ubuntu/.dsh/profiles/web/node_modules/@iasiv5/dsh-skills/package.json').version"`
- Expected: `1.0.0`

### Task 8: 本机迁移——清理 ~/.agents/skills 旧副本

> **状态（勘误 E，2026-11-01 13:48）：已由主人手动整体删除 `~/.agents/skills`（超计划范围、无备份）——以下 Step 1–5 作废留档。** 验收以勘误 E 缩略清单为准；lark-*×28 回迁待主人指示。

- 目标：消除 rank 500 对 rank 600 的遮蔽；`update.sh` 流对本机 DSH 退役。
- 涉及文件：`~/.agents/skills/`（仓外用户目录）；无仓内改动。
- 接口契约
  - Consumes: Task 7 装机验证通过（此前禁止清理）
  - Produces: 备份档案路径（供复发恢复）
- 验证范围：白名单 25 个仓管目录从 `~/.agents/skills/` 消失（24 插件收录 skill + `docs`），其余原样保留——**含 4 个许可剔除 skill 的本地副本（docx/pdf/xlsx/remotion-best-practices，插件不提供它们，本地保留即保持可用，勘误 D）**与 lark-* 等 28 个；新会话 18 项仍齐（来源切换为插件）。
- 事实注记：`~/.agents/skills` 本身是 update.sh 产出的 **git 工作树**（含 `.git`/`.gitignore` 及 `GLOSSARY.md`/`update.sh`/`.your-skill-collection.json` 等文件级副本）；B7 范围仅限**目录**，`.git` 与文件级残留不在本次删除集（见「计划外建议」）。

- [ ] Step 1: 全量备份
- Run: `tar -czf ~/workspace/.dsh-research/agents-skills-backup-20261101.tar.gz -C ~ .agents/skills`
- Expected: tarball 生成，`tar -tzf | head` 可列出内容
- [ ] Step 2: 按显式白名单删除。**仓管删除集 = 插件收录的 24 个 skill 目录（动态发现 − `PACKAGING_EXCLUDE`）+ `docs`，共 25 项白名单**；`docx`/`pdf`/`xlsx`/`remotion-best-practices` 与 `~/.agents/skills` 的 `.git` **显式保留/排除**（勘误 D）
- Run: 先 `comm -12 <(find ~/workspace/skills -mindepth 1 -maxdepth 1 -type d -not -name '.git' -not -name '.backup' -not -name 'docx' -not -name 'pdf' -not -name 'xlsx' -not -name 'remotion-best-practices' -printf "%f\n" | sort; echo docs) <(find ~/.agents/skills -mindepth 1 -maxdepth 1 -type d -printf "%f\n" | sort)` 预览交集 → 人工断言交集恰为 25 项（24 skill + `docs`）且不含 `.git` 与 4 个剔除项 → 逐目录 `rm -rf`
- Expected: 交集清单恰 25 项；出现 `.git`/4 个剔除项、缺项或多项 → 停下核对再删
- [ ] Step 3: 复核（显式断言，禁 `|| true` 吞退出码）
- Run: `WL="$( (find ~/workspace/skills -mindepth 1 -maxdepth 1 -type d -not -name '.git' -not -name '.backup' -not -name 'docx' -not -name 'pdf' -not -name 'xlsx' -not -name 'remotion-best-practices' -printf '%f\n'; echo docs) | sort)"; LEFT="$(comm -12 <(echo "$WL") <(ls ~/.agents/skills))"; [ -z "$LEFT" ] && [ "$(ls ~/.agents/skills | grep -c '^lark-')" = "28" ] && [ "$(ls -d ~/.agents/skills/docx 2>/dev/null | wc -l)" = "1" ] && echo PASS`
- Expected: 白名单 25 项**全部**不存在（`LEFT` 为空——全集逐项断言）；lark-* 恰 28 个；**4 个剔除 skill 本地副本仍在**（docx 抽查存在）；任一不符则非零退出并打印 `$LEFT`
- [ ] Step 4: 🔴 主人协同验证点——新会话 18 项 model 可见仍齐（来源 = 插件 rank 600）+ 4 个剔除 skill 本地斜杠仍可用（`/docx` 等，rank 500 本地副本）
- [ ] Step 5: checkpoint commit（如有 `update.sh` 注记未推，随下一批推送）

### Task 9: dsh-m 收录（audience internal）

- 目标：自家市场可装机、卡片标注「作者自用，不推广」。
- 涉及文件：Modify `~/workspace/dsh-m/registry.json`。
- 接口契约
  - Consumes: Task 7 装机事实（verified=0.2.1-rc.5）；Task 6 的 npm 包与 Task 4 的 icon（jsdelivr CDN URL：`https://cdn.jsdelivr.net/npm/@iasiv5/dsh-skills@1.0.0/icon.svg`）；id 已定稿 `dsh-skills`（主人批示 D3）；dsh-m 发版纪律（`dsh-m/AGENTS.md` Releasing 节 + know-how 018/031：`npm run release`、lock 三处同步、禁手打 tag、tag 须落在含 registry.json 的提交上）
  - Produces: dsh-m 卡片 `dsh-skills`（`dshm_search`/`dshm_install` 可见可装）
- 验证范围：`node scripts/validate-registry.mjs` 零警告；dsh-m 全量测试回到基线（028 §4）；**发版转正**（npm 新版 tarball 含条目——push ≠ 市场可见）。

- [ ] Step 1: registry.json 追加条目：`{"id":"dsh-skills","name":"DSH Skills (iasiv5)","description":"iasiv5 skill 合集（收录 24 个，另 4 个因上游许可未收录）的 DSH 插件化分发，bundled skill 方式加载，版本无关。作者自用，不推广。详见仓库。","category":"self-dev","tags":["skills","合集","bundled"],"audience":"internal","decoupled":true,"source":"npm","npm":"@iasiv5/dsh-skills","github":"iasiv5/skills","icon":"https://cdn.jsdelivr.net/npm/@iasiv5/dsh-skills@1.0.0/icon.svg","homepage":"https://github.com/iasiv5/skills","verified":["0.2.1-rc.5"]}`（id 已定稿，主人 2026-11-01 批示 D3 = `dsh-skills`；字段名以 registry 现有 internal 条目实测为准，Step 2 校验兜底）
- [ ] Step 2: 校验
- Run: `cd ~/workspace/dsh-m && export GITHUB_TOKEN=$(gh auth token) && node scripts/validate-registry.mjs`
- Expected: 零 error、零 warning（含 022 的 verified 污染告警）
- [ ] Step 3: dsh-m 全量测试对照基线
- Run: `cd ~/workspace/dsh-m && npm test`
- Expected: 失败集合 ⊆ 028 §4 既有清单（按 know-how 008，改名单需跑全量）
- [ ] Step 4: 🔴 主人确认后 push dsh-m（know-how 008：push 前经主人确认）
- [ ] Step 5: **dsh-m 发版**（registry.json 随 npm 包 `files` 分发——push ≠ 市场可见）：走 `npm run release`（含 lock 三处同步与 check-release 门禁；**禁手打 tag**，tag 必须落在含本次 registry.json 的提交上——2026-11-01 当天两次 CI 失败实录）；🔴 发版执行前主人确认
- Run: `cd ~/workspace/dsh-m && npm run release`（>90s 长命令走 `run_in_background`，日志落盘）
- Expected: npmjs 直查 `dsh-m` 出新版本号（know-how 018 staged 轮询纪律）；抽验新版 tarball 内 registry.json 含 `dsh-skills` 条目
- [ ] Step 6: 生效验证（依赖链：dsh-m 新版 → 宿主 dshm 升级 → 缓存刷新）：`dshm_upgrade`（dsh-m）→ `dshm_search` 搜 dsh-skills 出卡、`dshm_list` 可见
- Expected: 卡片带「作者自用」标注；宿主缓存（`~/.dsh/dshm/cache/`）刷新时机不完全可控——若延迟，以 Step 5 npm tarball 判据为最终事实、本机出卡随后补验（按章程声明该操作性判据的静态审阅覆盖度）

### Task 10: desktop 机（Host B）跟进清单（人工，非本机可执行）

- 目标：desktop 侧同款迁移的交接入场券。
- 交付物：本节即清单，执行在 Host B。
- [ ] 插件页按名安装 `@iasiv5/dsh-skills`（或 dsh-m Discover/市场入口）
- [ ] 完全退出托盘重开（desktop 重启语义）
- [ ] 新会话核对 18 项 model 可见 + 6 项斜杠可达（同 Task 5 Step 4 双清单）+ 日志无 `did not activate`
- [ ] 清理 `%USERPROFILE%\.agents\skills\`（或对应目录）中仓管 25 个目录（24 收录 skill + `docs`，先备份；同样排除 `.git`，保留 4 个许可剔除 skill 本地副本）
- [ ] 复验新会话 18 项来源为插件

## 执行纪律

- 开始实现前先批判性复查整份计划；发现缺项、矛盾、命令无效先修计划再动手。
- 按任务顺序执行，不无声跳步、合并或改目标；每任务跑完其验证再进下一个。
- 遇阻、重复失败、计划与仓库现实不符：立即停下说明，不猜。
- 🔴 标记的「主人协同验证点」必须真实完成并把证据记入执行摘要，不得代答。
- 当前仓库工作分支为 `main`；Task 6 合入与打标前先经主人确认（红灯纪律）。
- 所有 bash 长/联网命令遵循 web 机红线（npm cache、registry 直查、后台任务走 `run_in_background`）。
- `dshm_restart` 一律指 agent 工具调用；重启生效判据一律时间戳（轮询等待 ≤120s 防启动竞态）+ journal 联合探针。

## 最终验证（DoD，引用 Q9 共识；判据按评审 R1 修订）

1. 构建门禁绿：`cd dsh-plugin && npm run build && npm test` → `24 skills staged`（动态计数 == manifest 条数 == 24；排除行如实打印）、四门禁过（含 invocation 键门禁与 pack 禁入硬断言）、单测绿。
2. web 机装机后：journal 无 `did not activate` / `skipping profile bundle` **且** `ActiveEnterTimestamp` 较装机前推进（联合判据）；HTTP 200 仅辅助信号。
3. 主人新会话：本仓 **18 个 model-invocable skill 全部出现**在 available_skills（Task 5 Step 4 清单）；`/eli5` 冒烟成功（6 个 slash-only 之一）；6 个 `disable-model-invocation` skill 与 4 个许可剔除 skill（无本地副本的机器上）不在 catalog 属预期。
4. `~/.agents/skills/` 白名单 25 个仓管目录（24 收录 skill + `docs`）已清理、4 个剔除 skill 本地副本保留、备份 tarball 在 `~/workspace/.dsh-research/agents-skills-backup-20261101.tar.gz`；清理后复验 18 项仍齐。
5. dsh-m 发版转正：npmjs 上 dsh-m 新版 tarball 的 registry.json 含 `dsh-skills` 条目（可证判据）；registry validate 零警告；宿主 `dshm_search` 出卡（audience internal；依赖缓存刷新，延迟则以 npm 判据为准随后补验）。
6. desktop 清单（Task 10）交接给主人。

## 审阅 Checkpoint

计划正文到此为止。请审阅；批准后由普通编码 agent / 人工按序执行。
