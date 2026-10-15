# brainstorming skill 结构去重 实施计划

## 目标

- 对本地 `brainstorming` skill 做一轮 writing-great-skills **纯结构**优化：删除散文式复述、negation 黑名单与重复的响应模板，把唯一规则收敛到 single source of truth，微妙情境守卫 co-locate 到触发点。
- **契约：零行为变更**。每条被删/被移的规则必须在存活副本里找得到；PHASE 0–8 主干一行不动。
- 体量目标：303 行 / 16.9KB → 约 225–235 行 / 约 12.5–13KB（与 writing-plans 228/12.8KB 对齐）。

## 架构快照

- 主干 PHASE 0–8 不动。改动集中在主干之外的"脚手架"：失败模式表格、默认响应模板、反例黑名单、关键原则、description、CHECKPOINTS 的重复定义。
- 三段复制源（表格 + 模板 + 黑名单）合并/内联/删除为：**一个** writing-plans 式 `红灯与反例` 段（test-mapped 信号 + 显式 defer）。
- 微妙情境守卫用 `检索难度轴` 判据处理：co-locate 到触发 PHASE + leading-word 锚 + 测试用例兜底（测不过则前台化）。
- 复用 `plugins/iasi/skills/writing-plans/SKILL.md` 的"红灯与反例""关键原则单行"作为目标形态参照。

## 全局约束

- **纯结构、零行为变更**：每个删除点须先确认存活 single source；diff 审阅只问"这条在别处还活着吗"。
- **PHASE 0–8 一行不动**：本次不碰主干步骤与 completion criterion。
- **只改 brainstorming 一个 skill**：不动 writing-plans / handoff / cleanup（各自独立轮），不动上游冻结的 5 个 skill。
- **中模型校准**：删低密度散文复述，保留高密度锚词；定位用章节锚点字符串，行号仅作当前态提示（不作为唯一定位）。
- **English-token / conditional-approval 缺口本轮不做**（non_scope）。

## 输入工件

- 已批准设计：本会话 `/grill-with-docs` 共识（Q1–Q10 决策），无独立 spec 文档。
- 目标 skill：`plugins/iasi/skills/brainstorming/SKILL.md`（当前 303 行）。
- 形态参照：`plugins/iasi/skills/writing-plans/SKILL.md`。
- 术语/决策上下文：`GLOSSARY.md`、`docs/adr/0001-two-track-design-pull-only-plan-handoff.md`。

## 文件结构与职责

- Modify: `plugins/iasi/skills/brainstorming/SKILL.md` — 结构去重 + 守卫归位（Task 1）
- Modify: `plugins/iasi/skills/brainstorming/test-prompts.json` — 新增 3 条微妙守卫测试用例（Task 2）
- Modify: `GLOSSARY.md` — 新增 `检索难度轴` glossary 条目（Task 3）
- 验证：跨 3 文件的零行为丢失自检（Task 4）
- 收口：单条 commit（Task 5）

## 任务清单

### Task 1: 重构 brainstorming SKILL.md 脚手架（纯结构、零行为变更）

- 目标：把表格 / 模板 / 黑名单 / 关键原则 / description / CHECKPOINTS 重复定义收敛，守卫归位；PHASE 0–8 不动。
- 涉及文件：`plugins/iasi/skills/brainstorming/SKILL.md`
- 为什么是单任务：这些编辑互相依赖（红灯段替代表格、模板 blockquote 内联到删除位点、守卫归位与 re-inline 删除同处 PHASE2），拆分会产生不可独立验证的中间态。编辑按**章节锚点字符串**定位（非行号），顺序经安排以保持 diff 可读。
- 接口契约
  - Consumes：已批准设计（Q1–Q10）
  - Produces：重构后的 SKILL.md（PHASE 0–8 原样；`红灯与反例` 段、3 个内联 blockquote、3 条归位守卫就位）
- 验证范围：行数落到约 225–235；`grep` 确认每条被删规则仍有存活副本；PHASE 0–8 文本未变。

- [ ] Step 1: 改动前检查（基线快照）
  - Run: `cd plugins/iasi/skills/brainstorming && wc -l SKILL.md && grep -nE '^## ' SKILL.md`
  - Expected: 记录当前 303 行与章节标题清单，作为"PHASE 0–8 未变"的比对基线。
- [ ] Step 2: 改 description（frontmatter，锚点：`description:` 那一段）
  - Change: 替换为 `在开始实现前，把需求澄清成设计文档。适用于新增功能、修改行为、组件设计、接口设计、流程改造、架构取舍和多方案比较；即使任务看起来很简单，也先做简短设计；用户说"先想一下""先给方案""先规划一下""先比较两种做法"时优先使用。`（仅删末句"设计获批前不写代码"——与硬约束:33+引言三重重复；**保留"即使很简单也先做简短设计"**：description 是路由面，body 的"何时使用"要等路由后才加载，故该句不是路由期冗余，而是防小任务被跳过的锚——采纳评审 I3）。
- [ ] Step 3: 删 `## 反例黑名单` 整节（锚点：`## 反例黑名单` 到下一个 `##` 之前）
  - Change: 整节删除。存活副本已在硬约束 / 各 PHASE / CHECKPOINTS / spec-self-review；silent-drift 由 Step 8 归位，`<path>` 由 Step 9 归位。
- [ ] Step 4: 压 `## 关键原则`（锚点：`## 关键原则` 节）
  - Change: 8 行列表替换为单行：`One question · Multiple choice · YAGNI · Alternatives first · Incremental validation · Just-in-time visual · Isolation & clarity · Follow the repo（各词已在对应 PHASE 与硬约束里定义）`。
- [ ] Step 5: PHASE 8 加 `<path>` 守卫（锚点：`## PHASE 8` 下 handoff payload 代码块之后）
  - Change: 追加一行 `- payload 里的 \`<path>\` 等尖括号占位符必须替换成真实已批准路径，不要保留字面量`。
- [ ] Step 6: PHASE 5 入口加 silent-drift 守卫（锚点：`## PHASE 5: 写设计文档` 标题之后、路径选择之前）
  - Change: 插入 `> 无声漂移守卫：写文档时若偏离了 CHECKPOINT A 已批准的方案（范围、边界或关键取舍），把偏离点单独列出，回到用户面前重新触发 CHECKPOINT A 确认方向；未重确认前按已批准版本写，偏离写进未决事项。`
- [ ] Step 7: PHASE 7 去掉"套用模板 4"引用（锚点：`审批请求默认套用"模板 4：审批请求"`）
  - Change: 删该引用句（模板 4 内容与 PHASE 7 现有表述逐字重复，PHASE 7 保留即可）。
- [ ] Step 8: PHASE 2 内联首轮澄清示例 + 归位两条守卫 + 删 re-inline（锚点：`## PHASE 2: 一次一个问题地澄清` 节）
  - Change:（a）删除 PHASE 2 的整个 `规则：` 子块——含重抄 questioning-rules.md 的 3 条 **+** `- 首轮澄清默认套用"模板 1：首轮澄清"` 指针（删该指针避免 Step 11 删模板节后留孤儿；首轮形态由 (b) 内联 blockquote 取代），信任该节已有的 questioning-rules.md 指针；（b）追加内联示例 `默认形态：\n> 先把这次讨论收敛成设计文档，不进入实现。\n> （若跨子系统）这次需求可拆成 X / Y / Z；这轮只继续 X。\n> 先确认一个点：首要目标更偏 A / B / C？`；（c）追加两条归位守卫 `- 跨轮矛盾：用户跨轮次给出矛盾回答（如先选方案 A 又否定 A）→ 显式指出矛盾、引用前述具体选择，只问一个问题确认以哪轮为准；若用户确实改主意，回 PHASE 2-3 重做相关澄清，不假装没矛盾。` 与 `- 拒绝澄清：用户主动拒绝（"你决定吧""都行""你来定"）→ 点明缺哪个约束最致命，给 1 条最保守假设，只问一个问题确认是否接受；仍不给 → 按保守假设写边界级设计，假设与风险进未决事项。`
- [ ] Step 9: PHASE 3 内联方案比较示例 + 删模板 2 指针（锚点：`## PHASE 3: 提出 2-3 个方案` 节）
  - Change:（a）删除 PHASE 3 的 `- 输出默认套用"模板 2：方案比较"` 指针（避免 Step 11 后留孤儿；形态由 (b) 取代）；（b）节末追加 `默认形态：\n> 方案 A：……\n> 方案 B：……\n> 方案 C：……\n> 推荐方案：……\n> 先确认一个点：请回复 \`接受：推荐方案\`，或改选 \`接受：方案 A/B/C\`。`
- [ ] Step 10: 🛑 STOP 旁内联错误路由示例（锚点：`🛑 STOP · 错误路由` 那条之后）
  - Change: 追加 `默认形态：\n> 这一步不该继续用 brainstorming，应切到 \`writing-plans\`（或实现 / review 流程）。\n> 你现在要的是把已定需求拆成计划 / 直接编码 / 审查，不需要再做方案比较。`
- [ ] Step 11: 删 `## 默认响应模板` 整节（锚点：`## 默认响应模板` 到下一个 `##` 之前）
  - Change: 整节删除（其 4 个模板的默认形态已在 Step 8/9/10 内联；模板 4 与 PHASE 7 重复，直接随节删除）。
- [ ] Step 12: CHECKPOINTS 合并"同等明确"双定义（锚点：`## 🔴 CHECKPOINTS` 节内两段"判定"同等明确""）
  - Change: 两段合并为一段：`判定"同等明确"（🔴 CHECKPOINT A 与 B 通用）：必须明确点名所选方案（如"方案 A""推荐方案"）或批准的具体文档（如"批准刚才那份设计""就按 docs/specs/xxx 批准"），或使用确认令牌本身（\`接受：...\` / \`批准：<path>\`）；只表达整体态度（"看起来可以""先这样""应该行""你继续吧""好的""继续吧""都行"）而未点名的，一律视为模糊。半角冒号与全角冒号等价。`
- [ ] Step 13: `## 失败模式与回退` 整节替换为 `## 红灯与反例`（锚点：`## 失败模式与回退` 到下一个 `##` 之前）
  - Change: 替换为：
    ```
    ## 红灯与反例

    命中下列已知翻车点时按"信号 → 动作"处理，不要继续硬走流程：

    - **mixed intent（实现 + 设计混合）** → 不编码、不写补丁，只问一个路由选择题：`A. 这轮只做设计` / `B. 停止 brainstorming，直接进入实现或调试`
    - **直接写文档但方案尚未确认** → 先给推荐方案和 trade-offs 并触发 CHECKPOINT A；若用户只要草稿，文档标题显式标注"草稿 / 待审批"，不进入 `writing-plans`

    其余（设计未批准就写代码 / 含糊话术当 CHECKPOINT 批准 / 跨多子系统包装成一份巨设计 / 为"更干净"重做边界 / 路由 `writing-plans` 时重新澄清 / scope creep via doc / handoff payload 留字面量 `<path>` 等）已在硬约束、各 PHASE、🔴 CHECKPOINTS 与 `references/spec-self-review.md` 正面规定，此处不重复。
    ```
    （silent-drift 默认不进本段；仅当 Task 4 测试不过时，作为第三条信号 front 回来。）
- [ ] Step 14: 改动后验证
  - Run: `wc -l SKILL.md`（期望约 225–235）&& `grep -nE '^## ' SKILL.md`（期望章节：无 `失败模式与回退` / `默认响应模板` / `反例黑名单`；新增 `红灯与反例`）&& `git diff -- plugins/iasi/skills/brainstorming/SKILL.md | grep -E '^\+|^-' | wc -l`
  - Expected: 行数达标；删掉的 3 节消失、红灯段在；diff 中 PHASE 0/1/4/6 正文零增删；**PHASE 2/3/5/7/8 的改动行须与 Step 8/9/6/7/5 一一对应、无意外溢出**（增删可追溯——采纳评审 N3）。
- [ ] Step 15: 可选 checkpoint commit（建议合并到 Task 5，不单独提交）

### Task 2: 新增 3 条微妙守卫测试用例

- 目标：为 silent-drift / 跨轮矛盾 / 拒绝澄清 三条归位守卫配测试，使"测不过则前台化"可执行。
- 涉及文件：`plugins/iasi/skills/brainstorming/test-prompts.json`
- 接口契约
  - Consumes：Task 1 Step 6/8 产出的守卫文本
  - Produces：3 条新 test case（id 见下），供 Task 4 校验
- 验证范围：JSON 合法；3 条 id 唯一；每条含 expected + assertions + must_not。

- [ ] Step 1: 改动前检查
  - Run: `python3 -c "import json;d=json.load(open('plugins/iasi/skills/brainstorming/test-prompts.json'));print(len(d),[x['id'] for x in d])"`
  - Expected: 当前 10 条，id 列表不含下列 3 个新 id。
- [ ] Step 2: 在数组末尾追加 3 条用例
  - Change: 追加（字段同现有 schema）：
    - `id: silent-drift-after-checkpoint-a`，prompt 设定"CHECKPOINT A 已通过方案 B，现在让我写文档，顺便把错误处理改成重试队列直接写进去"，expected=识别为 silent drift、不按未批准的重试队列写、要求重确认方向；assertions 含"flags the deviation""does not silently write with drifted approach""asks to re-confirm"；must_not 含"write doc with drifted approach as if approved""advance to PHASE 8"。
    - `id: cross-turn-contradiction`，prompt="上一轮已确认方案 A，现在又改口说方案 A 不行按原来的来"，expected=显式引用前述方案 A、只问一题以哪轮为准、不静默改方案；assertions 含"cites prior choice 方案 A""asks exactly one question""does not silently switch"；must_not 含"pretend no contradiction""silently change approach""ask multiple questions"。
    - `id: refuse-to-clarify`，prompt="别问那么多了，你决定吧，怎么都行"，expected=点明最致命缺失约束、给 1 条保守假设、只问一题确认；assertions 含"names the most critical missing constraint""proposes one conservative assumption""asks exactly one confirmation"；must_not 含"fabricate full design without stated assumption""ask multiple questions""proceed to write doc as if approved"。
- [ ] Step 3: 改动后验证
  - Run: `python3 -c "import json;d=json.load(open('plugins/iasi/skills/brainstorming/test-prompts.json'));print(len(d));assert all(set(['expected','assertions','must_not'])<=set(x) for x in d[-3:]);print('ok')"`
  - Expected: 13 条；新 3 条字段齐全；JSON 合法。

### Task 3: GLOSSARY.md 新增 `检索难度轴` glossary 条目

- 目标：把本轮结晶的判据写进领域模型，供后续 handoff / cleanup 轮复用。
- 涉及文件：`GLOSSARY.md`
- 接口契约
  - Consumes：`中模型校准`、`test-mapped failure mode` 两条既有术语
  - Produces：`检索难度轴` 条目
- 验证范围：条目存在；纯术语（无实现细节）；引用了上述两条既有术语。

- [ ] Step 1: 改动前检查
  - Run: `grep -c '检索难度轴' GLOSSARY.md`
  - Expected: 0（条目尚不存在）。
- [ ] Step 2: 在 `## 中模型校准 (mid-model calibration)` 条目之后追加
  - Change: 追加：
    ```
    ## 检索难度轴 (retrieval-difficulty axis)

    salvage 一条 skill 规则时的判据：按"中模型在情境里能否检索到它"分两类。**微妙情境守卫**（如 silent drift、跨轮矛盾）——情境需先被识别再检索，中模型易漏，须 co-locate 到触发点 PHASE + leading-word 锚，并以测试用例验证；测不过则前台化为"信号 → 动作"。**泛化结构规则**（如多子系统拆分、可视化降级）——情境里易检索，直接 defer 到正面规则 single source 即可，重复才是病。本轴调和 `test-mapped failure mode`（保留信号）与 `中模型校准`（压缩非重复）的张力：要不要前台化重复一条规则，由检索难度决定。
    ```
- [ ] Step 3: 改动后验证（采纳 N4 + B2 修复）
  - Run: `grep -c '检索难度轴' GLOSSARY.md`（期望 ≥1）；再取新条目正文 `awk '/## 检索难度轴/{f=1;next} /^## /&&f{exit} f' GLOSSARY.md`（flag-awk：跳过标题行、到下一 `## ` 或 EOF——旧版 range awk `/A/,/^## /` 会因标题行自身匹配 `^## ` 而只输出标题、正文丢失，已实测确认），在其输出内 `grep -o '中模型校准\|test-mapped failure mode' | wc -l`（期望 ≥2，两条术语都被新条目显式引用，避免措辞微调丢引用）。
  - Expected: 检索难度轴条目存在；新条目正文内同时引用中模型校准与 test-mapped failure mode。

### Task 4: 零行为丢失自检（含 silent-drift front-back 判定）

- 目标：实证"纯结构、零行为变更"，并决定 silent-drift 是否需前台化。
- 涉及文件：只读 Task 1–3 产物
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md、Task 2 的 3 条新测试、Task 3 glossary
  - Produces：自检结论（pass / 需 front-back）
- 验证范围：下列 4 项全部通过。

- [ ] Step 1: 被删规则存活副本检查（位置敏感 + 孤儿断言）
  - Run:
    - 通用规则各跑 `grep -n`（一次只问一个问题 / 优先选择题 / 设计获批前不写代码 / 模糊话术不算批准 / scope creep / `<path>` 占位符）→ 期望在硬约束 / 对应 PHASE / 红灯段 / spec-self-review 至少 1 处存活。
    - 三条微妙守卫**位置敏感 + 锚词**断言（采纳 I1；O1 把"锚词钉死"并入本条，避免无 Run 的裸提醒）：`grep -nE '无声漂移' SKILL.md` 命中且**落在 PHASE 5**；`grep -nE '跨轮矛盾|拒绝澄清' SKILL.md` ≥2 处且**落在 PHASE 2**。命中数 ≥3 + 位置正确即隐含三个 leading word 已写入且未删除（"改写"属漏写，同样由 grep 覆盖）；位置敏感而非仅存在敏感，与 `检索难度轴` 的 co-locate 判据自洽。
    - 孤儿断言（采纳 B1，正则采纳 B3 加宽）：`grep -nE '套用.{0,3}模板' SKILL.md` 期望 **0 命中**（模板节已删，PHASE 2/3/7 指针全清；`.{0,3}` 容忍标点变体如全角引号/「」/空格+引号，避免换标点漏报——实测当前 3 处在 line 164/175/248，重构后应为 0）。
  - Expected: 上述全部通过。
- [ ] Step 2: PHASE 0–8 主干未变检查
  - Run: `git stash`（若已改）或对比基线快照——对 `## PHASE 0` 到 `## PHASE 8` 各节正文做 diff（排除 Step 5/6/7/8/9 的定点追加）。
  - Expected: 主干步骤与 completion criterion 无改动。
- [ ] Step 3: 三条 test-mapped 行为仍可触发检查
  - Run: 人工走查 happy-path #1（one question）、ambiguous-approval #5（含糊话术）、mixed-intent（红灯段第 1 条）在新 SKILL.md 下的触发路径。
  - Expected: 三条都能由新文本导出原 expected 行为。
- [ ] Step 4: silent-drift front-back 判定（本环境不可执行，预设默认——采纳 I2）
  - 现状声明：本环境无 model eval harness，Task 2 的 `silent-drift-after-checkpoint-a` 无法自动跑；"不可靠 → 前台化"分支**当前不可触发**，不伪装成 live gate。
  - 默认结论：保持 co-located（PHASE 5 入口守卫 + leading-word 锚），**红灯段不加第三条信号**。理由：守卫已 co-locate 到触发点 + Task 2 配了测试用例（供将来 darwin full_test 或 eval harness 消费），满足 `检索难度轴` 的 co-locate + 锚 + 测试三件套。
  - 复评门槛：将来接入 eval harness 后，若该用例失败率 > 20%，回到 Task 1 Step 13 把 silent-drift 作为第三条 `**无声漂移** → …` 信号 front 回来，并保留 PHASE 5 守卫。
  - 把默认结论与门槛记入 commit message，供后续 cleanup 轮追溯。

### Task 5: 收口 commit

- 目标：一条 commit 记录本轮结构去重。
- 涉及文件：3 个改动文件
- 接口契约
  - Consumes：Task 1–4 全通过
  - Produces：git commit
- 验证范围：commit message 说明零行为变更 + 检索难度轴 + 三条守卫测试。

- [ ] Step 0: 计划文档归属（采纳 N1）
  - Change: 本计划文档当前未跟踪。在执行开始前先单独提交：`git add docs/plans/2026-07-25-brainstorming-structural-dedup-implementation-plan.md && git commit -m "docs(plans): brainstorming 结构去重实施计划"`。计划先于改动落盘，便于追溯；Task 5 的工作提交只含 3 个工作文件。
- [ ] Step 1: 暂存与提交
  - Run: `git add plugins/iasi/skills/brainstorming/SKILL.md plugins/iasi/skills/brainstorming/test-prompts.json GLOSSARY.md && git commit`
  - Change: message 参照 writing-plans 风格，如 `brainstorming: 结构去重（红灯段合并 + 模板内联 + 守卫归位）`，正文记：删表格/模板/黑名单 → 单个红灯段、关键原则压一行、description 剪尾、同等明确合一、3 守卫 co-locate+测试、新增检索难度轴 glossary、silent-drift front-back 结论；footer `Co-Authored-By: Claude <noreply@anthropic.com>`。
  - Expected: commit 成功；`git status` clean。

## 执行纪律

- 开始实现前先复查整份计划；发现缺项、矛盾或锚点失配先修计划。
- Task 1 内按 Step 编号顺序执行（已安排避免锚点漂移）；定位一律用章节锚点字符串，行号仅作提示。
- 每个 Step 的"改动后验证"必须实际跑，不要跳过。
- 遇到删除后某条规则找不到存活副本，立即停下补归属，不要留孤儿。
- 若当前在 `main` 且用户未明确同意，提交前先确认分支策略（采纳 N2 + O2 nuance）。注：e76bbdb 系列虽直推 `main`，但彼时是上游冻结 skill 的本地适配（同步已评审改动）；本次 brainstorming 是**本地 skill 自主大规模重构**，性质略重——倾向 Task 5 前征得用户明确同意后再沿用 main，或新建 feature 分支。不默认静默提交到 main。

## 最终验证

- `wc -l plugins/iasi/skills/brainstorming/SKILL.md` → 约 225–235 行。
- `grep -nE '^## ' …/SKILL.md` → 无 `失败模式与回退` / `默认响应模板` / `反例黑名单`；有 `红灯与反例`。
- `python3 -c "import json;json.load(open('plugins/iasi/skills/brainstorming/test-prompts.json'))"` → 合法，13 条。
- `grep -c '检索难度轴' GLOSSARY.md` → ≥1。
- Task 4 的 4 项全 pass（含 silent-drift front-back 结论已记）。
- `git log -1 --stat` → 单 commit，3 文件。

## 审阅 Checkpoint

- 计划正文结束。请审阅；未获批准不进入实现。
- **待用户终判的 open items**（执行前必须闭环，采纳 I4）：
  1. **I3 description 取舍**：Task 1 Step 2 反转了 grill 阶段 Q6 的原批准。默认按修订版（保留"即使很简单也先做简短设计"、仅删"不写代码"）；若用户维持 Q6 原批准（两句全删），Step 2 改回原批准执行。Step 2 的 Change 已给完整新 description 字面量，执行时整段替换、勿逐句删以免误删保留分句。
  2. **分支策略（N2/O2）**：e76bbdb 系列虽直推 main，但彼时是上游冻结 skill 的本地适配，本次 brainstorming 是本地 skill 自主大规模重构（性质略重）——沿用 main 既有约定，还是新建 feature 分支，需用户裁决。
- 若批准，按 Task 1 → 2 → 3 → 4 → 5 顺序执行；Task 4 Step 4 的 front-back 结论会在实施时回报。
