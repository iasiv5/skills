# writing-plans skill 第二轮结构去重 实施计划

> v3（2026-07-25）：吸收评审第二轮。P0-R——Task 1 Step 2 MERGE-A 原把 L60 逐字并入，连带把"或读完后仍无法确定范围"带进新分支，与 PHASE 0 L83-85「范围不明」分支语义重叠（v2 自造 redundancy）；裁到只剩 L60 独有路径级触发，scope 交还既有分支。P1-R1——commit body 补 MERGE-B 取舍说明。P2-R1——体量复算约 214。P2-R2——Task 3 Step 2 补 darwin judge prompt 模板。评审 v1 嘴硬的 L85/footer/L64-73 三点已自查 grep 推翻撤回，确认。
>
> v2（2026-07-25）：吸收评审 Agent 第一轮报告。主要修订——Task 1 由"删 STOP 段、PHASE 0 不动"改为"**先 MERGE 再 DELETE**"（P0-1：L60 触发条件在 PHASE 0 无副本；P1-1：fork 锚词密度流失）；darwin judge 输出去掉 per-dim keep/revert、改主 agent 整合（P0-3）；A/B 落 repo-local `.darwin/`、judge 自读 rubric（P1-2）；baseline 措辞修正（P1-3）；孤儿扫描加宽（P1-4）；Task 4 加框架冲突判据表（P2-1）；results.tsv note 单行（P2-2）；全局约束声明不动 test-prompts（P2-3）。

## 目标

- 对本地 `writing-plans` skill 做第二轮 writing-great-skills **纯结构**去重：把散落在红灯段 + STOP 段 + PHASE 0 的同一条 STOP 规则收敛到 single source of truth，红灯段升级为 brainstorming 桥接后的三段式诊断索引表。
- **契约：零行为变更**。每条被删/被移的规则必须在存活副本里找得到；PHASE 0–6 的**步骤结构与 completion criterion 不动**。PHASE 0 的输入校验 handler 区允许吸收被删 STOP 段的 L60 触发条件与 fork 触发情境锚词（P0-1 + P1-1）——这是 single-source-of-truth 的必要合并，规则仍照常触发，不是行为变更。
- 体量目标：227 行 → 约 212–218 行（P2-R1 复算约 214）。明细：MERGE-A 裁后 ≈ +2 行、MERGE-B 同行替换 ≈ 0、删独立 STOP 段 ≈ −11 行、瘦路由 fork ≈ −2 行、红灯段转索引表 ≈ −2 行，净减约 9–15 行。
- darwin 目标：dim3（失败模式编码，索引表三段式）/ dim7（结构，去重）不降反升；dim9（黑名单）靠 4 条 test-mapped 信号在索引表存活而 hold（不预期升——本轮不补 test-prompts）。

## 架构快照

- 主干 PHASE 0–6 的步骤结构与 completion criterion 不动。改动集中在主干之外的"脚手架"：独立的"🔴 CHECKPOINT / 🛑 STOP 规则"段、"红灯与反例"段、"不要路由到 writing-plans"段的 fork，外加 PHASE 0 输入校验 handler 区的必要合并。
- **MERGE then DELETE**（替代原"删 + 不动"）：独立 STOP 段有两条独有内容必须先并入 PHASE 0 才能无损删除——
  - **L60 独有触发条件**（"用户给出设计文档路径但表达不确定、文件不存在、不可读"）：实测全文只在 L60 出现一次，PHASE 0 无副本（P0-1）。并入 PHASE 0 作为新的输入校验"如果"分支，**触发条件只裁到 L60 独有的路径级失败**——不含"或读完后仍无法确定范围"（那部分由 PHASE 0 既有 L83-85「范围不明」分支承接），避免造出与既有分支语义重叠的第 4 个 if（P0-R）。
  - **L57-59 fork 触发情境锚词**（brainstorming 的"还在比较方案/目标边界没钉住"、grill-with-docs 的"已有想法或草稿/沉淀 ADR glossary"等）：PHASE 0 现有 fork（L81）措辞比 STOP 段粗糙，删 STOP 段会丢这些压缩锚词（P1-1）。并入 PHASE 0 的 fork 行，使唯一家持全密度。
  - 并入后，独立 STOP 段的 5 条全部有家：4 条输入校验 STOP 在 PHASE 0（3 条既有 + L60 新并入），1 条 CHECKPOINT 在 PHASE 6。此时删除独立 STOP 段才是真正零行为丢失。
- 红灯段从"信号→动作（动作完整重述）"两段式，升级为 brainstorming 桥接后的"信号→一线动作→详见"三段式**诊断索引表**：动作不重述，只指指针——同时解 dim3（两段式 gap）与 dim7（STOP overlap）。
- 形态参照：`plugins/iasi/skills/brainstorming/SKILL.md` 的"红灯与反例"表（该表在 brainstorming 文件 L64-73 区）。
- 不动：description（路由面敏感）、入口身份句（dedup 轮不碰身份锚）、test-prompts.json（F3 延后 round-3）、GLOSSARY.md / docs/adr/（Q1 决策不达 ADR 三全门槛，无新术语）。

## 全局约束

- **纯结构、零行为变更**：每个删除点须先确认存活 single source；MERGE 优先于 DELETE——独有内容先并入存活家，再删冗余段。
- **PHASE 0–6 步骤结构与 completion criterion 不动**；PHASE 0 输入校验 handler 区的例外：允许吸收被删 STOP 段的 L60 触发条件（新增一个"如果"分支）与 fork 触发情境锚词（充实既有 fork 行）。这是合并不是改写，规则触发行为不变。
- **本轮不动 test-prompts.json**：5 条偏少是已知缺口（brainstorming 13 条），留待 round-3 配合失败模式反例补强；darwin dim9 预期 hold（8），不预期升。
- **只改 writing-plans 一个 skill**：不动 brainstorming / handoff / cleanup，不动上游冻结的 5 个 skill。
- **中模型校准**：删低密度复述，保留高密度锚词；定位用章节锚点字符串，行号仅作当前态提示（不作为唯一定位）——本计划正文行号为 v2 实测值（grep 锁定），执行时仍以锚点字符串为准。
- **darwin 硬约束**：跨 judge 总分不可比，只信 within-judge delta（blind A/B 同评两版）；judge 不被告知重点 dim、不注入 rubric 正文、不输出 keep/revert（keep/revert 由主 agent 跨 judge 整合）；dim8 实测必须 spawn 独立 Agent 子 judge，禁主 agent 自评；results.tsv 用 Python 追加（9 字段、note 单行 `;` 分隔、assert 无 tab）；结果卡交付 HTML（本 WSL 无 PNG 渲染）。
- **分支**：feature 分支 `writing-plans-round2`，--no-ff merge 回 main。commit footer 沿用仓库既有惯例 `Co-Authored-By: Claude <noreply@anthropic.com>`（实测 e76bbdb 等一致）。

## 输入工件

- 已批准设计：本会话 `/grill-with-docs` 共识（Q1–Q3 决策）+ 评审 Agent 报告（P0/P1/P2）。
- 目标 skill：`plugins/iasi/skills/writing-plans/SKILL.md`（当前 227 行）。
- 形态参照：`plugins/iasi/skills/brainstorming/SKILL.md`（红灯段索引表）。
- 诊断 rubric：`~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md`。
- 术语/决策上下文：`GLOSSARY.md`（检索难度轴、test-mapped failure mode、中模型校准）、`docs/adr/0001-two-track-design-pull-only-plan-handoff.md`。
- handoff：`docs/handoff/2026-07-25-writing-plans-round2-handoff.md`（9 个硬约束）。

## 文件结构与职责

- Modify: `plugins/iasi/skills/writing-plans/SKILL.md` — MERGE+去重（Task 1）
- Modify: `plugins/iasi/skills/writing-plans/.gitignore`（新建或追加）— 忽略 `.darwin/` 临时评分文件（Task 3）
- 验证：零行为丢失自检（Task 2，只读）
- darwin 实测：≥2 独立 judge 盲评 A/B（Task 3，只读 + results.tsv 追加）
- 视情况桥接（Task 4，条件触发）
- 收口：feature 分支 commit + --no-ff merge（Task 5）

## 任务清单

### Task 1: MERGE then DELETE——重构 writing-plans SKILL.md 脚手架（纯结构、零行为变更）

- 目标：先把独立 STOP 段的独有内容（L60 触发条件 + fork 锚词）并入 PHASE 0，再删冗余的独立 STOP 段；红灯段转三段式索引表；瘦路由 fork。PHASE 0–6 步骤结构与 completion criterion 不动。
- 涉及文件：`plugins/iasi/skills/writing-plans/SKILL.md`
- 为什么是单任务：MERGE 与 DELETE 强依赖——红灯索引表的"详见"指针指向并入后的 PHASE 0 handler（含 L60 新分支）；CHECKPOINT 折叠依赖 STOP 段删除；路由 fork 瘦身依赖 PHASE 0 成为唯一 fork 家。拆分会产生引用断链的中间态。编辑按**章节锚点字符串**定位（非行号），顺序经安排以保持 diff 可读。
- 接口契约
  - Consumes：已批准设计（Q1–Q3）+ 评审 P0-1/P1-1
  - Produces：重构后的 SKILL.md（PHASE 0–6 步骤结构原样；PHASE 0 多一个 L60 路径分支 + 充实 fork；独立 STOP 段消失；红灯段为索引表；路由 fork 瘦身）
- 验证范围：行数落到约 212–218；存活副本 grep 同时验**触发条件 + 动作**（P0-1）+ P0-R 无新造重叠；PHASE 0–6 步骤结构未变。

- [ ] Step 1: 改动前检查（基线快照）
  - Run: `cd plugins/iasi/skills/writing-plans && wc -l SKILL.md && grep -nE '^## |🛑 STOP' SKILL.md`
  - Expected: 227 行；章节含 `## 🔴 CHECKPOINT / 🛑 STOP 规则`（L53）、`## 红灯与反例`（L33）；STOP 命中 L56/60/61/62（独立段）+ L74/79（PHASE 0）+ L85（PHASE 0 引用）。记录为比对基线。

- [ ] Step 2: MERGE-A——把 L60 独有触发条件并入 PHASE 0（P0-1 + P0-R）
  - 锚点：PHASE 0 第二个"如果"分支（"如果输入仍然存在明显的方案未定..."，含 Step 3 充实后的 fork 行）**之后**、第三个"如果"分支（"如果还不知道关键路径..."）**之前**（放在「范围不明」分支上方，使下方"参见"指向成立）。
  - Change: 追加一个新的输入校验"如果"分支（**只吸收独立 STOP 段 L60 的独有触发条件**——路径本身表达不确定/不存在/不可读；**不含**"读完后仍无法确定范围"，那部分由下方既有「不知道关键路径」分支承接，P0-R）：
    ```
    如果用户给出的设计文档路径表达不确定、文件不存在或不可读：
    - 🛑 STOP：说明缺口，不猜路径、不猜命令，不生成完整计划（路径可读但范围/验证方式仍不明的情况，见下方"不知道关键路径"分支）
    ```
  - 理由：实测 `文件不存在|不可读|表达不确定` 全文原只 L60 一处；并入 PHASE 0 后，删 STOP 段才是零行为丢失。test-prompts `missing-design-path-stop` 的"检查设计文档是否存在/路径不存在"由这个新分支承接。触发条件只裁到 L60 独有的路径级失败，避免与 L83-85 既有「范围不明」分支语义重叠、不造第 4 个冗余 if（P0-R）。

- [ ] Step 3: MERGE-B——充实 PHASE 0 的 fork 行（P1-1）
  - 锚点：PHASE 0"如果输入仍然存在明显的方案未定、关键约束缺失或逻辑矛盾"分支下、以"选一条设计轨道补设计"开头的那一行（实测 L81）。
  - Change: 该行替换为充实版（吸收独立 STOP 段 L57-59 的触发情境锚词，使唯一家持全密度）：
    ```
    - 选一条设计轨道补设计——`brainstorming`（还在比较方案 / 需要多选澄清 / 目标边界没钉住时）、`grill-with-docs`（已有想法或草稿 / 对抗式压力测试 / 顺带沉淀 ADR glossary 时）、或直接补一份更清晰的需求（只是缺几条约束 / 不必走完整设计流程时）
    ```
  - 理由：原 PHASE 0 fork 措辞比 STOP 段粗糙；删 STOP 段前把锚词并入，避免 dim5（模板具象）/ dim3（情境→动作）密度流失。

- [ ] Step 4: DELETE——删整段独立 `## 🔴 CHECKPOINT / 🛑 STOP 规则`（锚点：`## 🔴 CHECKPOINT / 🛑 STOP 规则` 到下一个 `## ` 即 `## PHASE 0` 之前）
  - Change: 整段删除（实测 L53-63）。存活副本核查（MERGE 后）——设计未批准/三选 fork → PHASE 0"方案未定"分支（L78-81 区，Step 3 已充实）；编造路径/文件不存在 → PHASE 0 新路径分支（Step 2）；多子系统 → PHASE 0"多子系统"分支（L73-76 区）；说不清范围 → PHASE 0"不知道关键路径"分支（L83-85 区）；CHECKPOINT（自检后审阅、未批准不实现）→ PHASE 6 整段（L194-210）。5 条全部有家。
  - 孤儿注意：PHASE 0"按上面的 🛑 STOP 规则停下"（L85）指的是 PHASE 0 自身的 STOP（L74、L79），不指被删独立段——删除后语义不变，无需改（Task 2 Step 2 复验）。

- [ ] Step 5: 替换整段 `## 红灯与反例`（锚点：`## 红灯与反例` 到下一个 `## ` 即 `## 硬约束` 之前）
  - Change: 替换为三段式诊断索引表：
    ```
    ## 红灯与反例

    命中下列已知翻车点时按"信号 → 一线动作"先处理，再跳到"详见"里的处理器。本表是**诊断索引**——每条只写一线动作并指向详细规则归属，不在此重复正文：

    | 信号 | 一线动作 | 详见 |
    |---|---|---|
    | 设计未批准 / 方案未定就硬写计划（`unapproved-design-stop`） | 🛑 STOP，走三选 fork（`brainstorming` / `grill-with-docs` / 补需求） | PHASE 0（方案未定分支） |
    | 编造文件、命令或测试框架（`missing-design-path-stop`） | 🛑 STOP，说明缺口，不猜路径、不猜命令 | PHASE 0（路径分支）、PHASE 1 |
    | 一个请求横跨多个独立子系统（`multi-subsystem-split`） | 🛑 STOP，先拆成多份计划，每份独立可验证 | PHASE 0（多子系统分支） |
    | 跳过文件结构直接列任务（`skip-file-structure-first`） | 回 PHASE 2 先规划文件结构与职责 | PHASE 2 |

    其余（不要占位符 / 不要省略接口契约 / 交接终点是 handoff 等）已在硬约束与各 PHASE 里正面规定，此处不重复。
    ```
    - 保留 4 个 test-mapped id（失败模式编码，dim9 奖励显式编码，映射 test-prompts.json）。
    - "详见"列指向 MERGE 后的 PHASE 0 分支（含 Step 2 新路径分支）。

- [ ] Step 6: 瘦"不要路由到 writing-plans"段的 fork（锚点：`如果还没有批准过的设计或达成共识，选一条设计轨道做扎实：` 那一句）
  - Change: 该句（现为 brainstorming + grill-with-docs 二选带提示）替换为一行指针：`如果还没有批准过的设计或达成共识，走 PHASE 0 的"方案未定"三选 fork（brainstorming / grill-with-docs / 补需求）。`
  - 理由：fork 全量（含触发情境锚词）的唯一家是 PHASE 0（Step 3 充实）；路由面只需一行点名 + 指针。

- [ ] Step 7: 改动后验证
  - Run: `wc -l SKILL.md`（期望约 212–218）&& `grep -nE '^## ' SKILL.md`（期望章节：无 `🔴 CHECKPOINT / 🛑 STOP 规则`；`红灯与反例` 在）&& `sed -n '/## PHASE 0:/,/## PHASE 1/p' SKILL.md | grep -cE '🛑 STOP'`（期望 **4**：3 个真 STOP bullet——多子系统/方案未定/新路径 + L85"按上面的 🛑 STOP"段内引用；P3-4，评审原说 3 漏算 L85 引用，实测为 4）&& 存活副本 + 孤儿扫描（见 Task 2）。
  - Expected: 行数达标；STOP 段消失、红灯段索引表在；PHASE 0/1/2/3/4/5/6 步骤结构与 completion criterion 零改动（diff 增删仅落在 Step 2/3/4/5/6 位点）。

### Task 2: 零行为丢失自检

- 目标：实证"纯结构、零行为变更"，**同时验触发条件 + 动作**（P0-1 修补的自检口径）。
- 涉及文件：只读 Task 1 产物
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md
  - Produces：自检结论（pass / 需补归属）
- 验证范围：下列 3 项全部通过。

- [ ] Step 1: 被删 STOP 规则存活副本检查（触发条件 + 动作，位置敏感）
  - Run:
    - L60 触发条件：`grep -nE '文件不存在|不可读|表达不确定' SKILL.md` → 期望命中且**落在 PHASE 0**（Step 2 新路径分支），红灯段索引表只一行一线动作、不出现这些触发词。
    - P0-R 复验（无新造重叠）：`grep -nE '读完后.{0,6}无法确定|或读完后' SKILL.md` → 期望 **0 命中**（scope 重叠子句已从新路径分支裁掉；"范围不明"只由 L83-85 既有分支用"还不知道关键路径/补完最小上下文后仍然说不清"措辞持）。
    - fork 触发情境锚词：`grep -nE '还在比较方案|目标.{0,2}边界没钉住|已有想法或草稿|沉淀 ADR' SKILL.md` → 期望命中且**落在 PHASE 0**（Step 3 充实 fork 行），不在别处。
    - 多子系统 handler：`grep -nE '多个独立子系统|多份计划' SKILL.md` → 期望 handler 落在 PHASE 0"多子系统"分支，红灯段索引表一行。
    - CHECKPOINT handler：`grep -nE '请求用户审阅|未获批准.*不进入实现|不进入实现' SKILL.md` → 期望落在 PHASE 6。
  - Expected: 4 条输入校验 STOP 各自的**触发条件 + 动作**唯一落在 PHASE 0；CHECKPOINT 唯一落在 PHASE 6；红灯段索引表只持一线动作 + 指针，不重述触发条件。

- [ ] Step 2: 孤儿指针扫描（加宽，P1-4）
  - Run: `grep -nE 'STOP 规则段|上方 STOP|见 STOP|参见.*STOP 规则|上面的.*STOP|前述.*STOP|参见.*CHECKPOINT' SKILL.md`
  - Expected: 仅命中 PHASE 0"按上面的 🛑 STOP 规则停下"（v2 实测 L85）一处——该处是**合法的 PHASE 0 段内引用**（指向同段 L74/L79 的 STOP），不是指向已删独立段的外指孤儿。逐 hit 核对：每个命中都须指向段内或存活段，0 外指孤儿。

- [ ] Step 3: PHASE 0–6 步骤结构未变检查
  - Run: `git diff -- plugins/iasi/skills/writing-plans/SKILL.md`，逐 hunk 核对——增删行须全部落在 Step 2（PHASE 0 新路径分支）/ Step 3（PHASE 0 fork 充实）/ Step 4（删 STOP 段）/ Step 5（红灯段替换）/ Step 6（路由 fork 瘦身）五个位点。PHASE 0 既有三个"如果"分支的步骤骨架、PHASE 1/2/3/4/5/6 正文与 completion criterion 零改动。
  - Expected: 主干步骤结构与 completion criterion 无改动；diff 可追溯到 Step 2-6。

### Task 3: darwin full_test 实测（blind A/B）

- 目标：用独立 judge 盲评改后(B) vs 改前(A)，within-judge delta 验证 dim3/dim7 不降、dim9 hold。
- 涉及文件：只读 SKILL.md（A/B 两版落 `.darwin/`）；追加 `results.tsv`
- 接口契约
  - Consumes：Task 1–2 通过
  - Produces：≥2 judge 的 per-dim 双分数 + Δ；results.tsv 新行
- 验证范围：≥2 独立 Agent 子 judge；每个 judge 同评 A/B 两版；judge 不被告知重点 dim、不注入 rubric、不输出 keep/revert。

- [ ] Step 1: 落 A/B 两版到 repo-local 临时文件（P1-2）
  - Run:
    - `mkdir -p plugins/iasi/skills/writing-plans/.darwin`
    - A 版：`git show HEAD:plugins/iasi/skills/writing-plans/SKILL.md > plugins/iasi/skills/writing-plans/.darwin/wp_A.md`（round-2 改前 227 行版）
    - B 版：`cp plugins/iasi/skills/writing-plans/SKILL.md plugins/iasi/skills/writing-plans/.darwin/wp_B.md`（Task 1 产物）
    - 确保 `.darwin/` 在 `.gitignore`（新建或追加一行 `.darwin/`）；不用裸 `/tmp`（WSL sandbox TMPDIR 风险）。
  - Expected: 两版文件就绪；`.darwin/` 不入 git。

- [ ] Step 2: spawn ≥2 独立 judge（Agent 工具，独立 context，blind）
  - Run: 每个 judge 的 prompt **只给两个文件路径** `wp_A.md` / `wp_B.md`，**不告诉哪个是改前/改后、不点名重点 dim、不注入 darwin rubric 正文**（让 judge 自己读 `~/.claude/skills/darwin-skill/SKILL.md` 的 9-dim rubric）。要求每个 judge 按 9-dim 全评两版，输出**每维 A_score、B_score、Δ(B−A)**，**不要给 keep/revert 结论**。
  - prompt 模板（P2-R2，spawn 时照填，只换 judge 编号）：
    ```
    读取以下两份 SKILL.md（标记 A 和 B，身份未知，不要假设哪个是改前/改后）：
      A: plugins/iasi/skills/writing-plans/.darwin/wp_A.md
      B: plugins/iasi/skills/writing-plans/.darwin/wp_B.md
    按 ~/.claude/skills/darwin-skill/SKILL.md 描述的 9-dim rubric（dim1-dim9）各评两版，
    输出 markdown 表格：| dim | A_score | B_score | Δ(B−A) | 简评 |
    不要给 keep/revert 结论；不要预设重点 dim。
    ```
  - 硬约束：禁主 agent 自评（darwin 反例 #1）；judge 盲评不知 A/B 身份；keep/revert 不在 judge 做。
  - Expected: ≥2 份独立 per-dim 双分数 + Δ。

- [ ] Step 3: 主 agent 跨 judge 整合 keep/revert（P0-3）
  - Run: 主 agent 汇总 ≥2 judge 的 per-dim Δ，看方向一致性。重点 dim（dim3/dim7/dim9——由主 agent 事后识别，judge 不知情）判据：Δ 不显著为负（> −1）即 keep；若 ≥2 judge 在同一重点 dim 方向一致判定显著为负（≤ −1），触发 Task 4。
  - Expected: 给出 keep / 触发 Task 4 的整合结论 + 依据。

- [ ] Step 4: 追加 results.tsv（Python，9 字段，note 单行）
  - Run: Python 追加一行，字段 = `timestamp \t commit \t writing-plans \t old_score \t new_score \t status \t dimension \t note \t eval_mode`；每字段 `assert '\t' not in f`；note **单行**用 `;` 分隔多段（禁换行/tab）；`write('\n'.join(lines)+'\n')`；末行列数 = 9。
  - note 记录：`round2 MERGE+去重(删STOP段+红灯索引表+路由fork瘦身+PHASE0吸收L60/fork锚词); within-judge delta per dim 见 commit body; dim3/dim7/dim9 判定 X; 独立judge盲评full_test`。delta 详细数据写 commit message body（不入 tsv），body 骨架（P3-3，参照 e76bbdb bullet 风格）：
    ```
    darwin full_test（n=2 独立 judge 盲评 A/B）
    - judge1 per-dim Δ：dim1..dim9 = [Δ 列表，合并成一行]
    - judge2 per-dim Δ：dim1..dim9 = [Δ 列表，合并成一行]
    - 经主 agent 跨 judge 整合：dim3/dim7 不降、dim9 hold（Δ > −1），keep
    ```
  - Expected: results.tsv 合法追加，9 列，note 单行。

### Task 4: 视情况桥接（条件触发，附框架冲突判据表 P2-1）

- 目标：若 darwin 出现任一重点 dim 的 within-judge delta 显著为负且整合判 revert，用诊断索引表 + co-located 守卫桥接后再复测。
- 触发条件：Task 3 Step 3 整合判定 revert（≥2 judge 同一重点 dim 方向一致显著为负）。
- 涉及文件：视情况 Modify SKILL.md + 复测
- 接口契约
  - Consumes：Task 3 delta 信号
  - Produces：桥接版（若触发）+ 复测 delta
- 验证范围：若触发，桥接后再跑 Task 3 Step 2 复测，within-judge delta 转正或 hold。

- [ ] Step 1: 诊断负 delta（框架冲突判据表）
  - 判据：
    | 负 delta 的 dim | 与本轮改动关系 | 判定 |
    |---|---|---|
    | dim7（结构/整体架构） | 直接对应（去重） | 预期升；若降 = **真退化**（删错了/留孤儿）→ 回 Task 1/2 补归属 |
    | dim3（失败模式编码）/ dim9（反例黑名单） | 框架冲突区（darwin 奖励显式表/黑名单，WGS 要删） | 若降 = **框架冲突** → 走 Step 2 桥接 |
    | dim1/2/4/6（与去重无关） | 间接 | 若降 = judge 噪声/方差；除非 ≥2 judge 一致，否则 disregard |
  - Expected: 区分真退化 / 框架冲突 / 噪声；真退化回 Task 1/2，框架冲突走 Step 2，噪声 disregard。

- [ ] Step 2: 桥接（仅框架冲突）
  - Change: 用"诊断索引表（信号→一线动作→详见指针，不重述）+ 保留 co-located 守卫作真正处理器"桥接（参照 brainstorming `5f54f04` 桥接配方）。本轮已预先采用索引表形态 + PHASE 0 co-located handler，预期框架冲突风险低；若 dim3/9 仍触发，补强"详见"指针或保留某条 co-located 守卫。
  - Expected: 桥接版就绪，复测 delta 转正/hold。

### Task 5: 收口（feature 分支 + commit + --no-ff merge）

- 目标：在 `writing-plans-round2` 分支收口，--no-ff merge 回 main。
- 涉及文件：SKILL.md + results.tsv（+ .gitignore + 本计划文档）
- 接口契约
  - Consumes：Task 1–4 全通过（darwin keep）
  - Produces：feature 分支 commit + main 上 --no-ff merge
- 验证范围：commit message 说明 MERGE+去重 + 零行为变更 + darwin delta；merge 保留评审脉络。

- [ ] Step 0: 分支与计划文档归属
  - Change: 执行开始前先建分支并落计划：`git checkout -b writing-plans-round2` → `git add docs/plans/2026-07-25-writing-plans-round2-structural-dedup-implementation-plan.md && git commit -m "docs(plans): writing-plans round2 结构去重实施计划（经三轮评审落地）"`（commit message 去版本号——版本号是评审过程产物，merge 进 main 后会过时；参照 e76bbdb 无版本号风格，P3-2）。计划先于改动落盘。
- [ ] Step 1: 暂存与提交（工作改动）
  - Run: `git add plugins/iasi/skills/writing-plans/SKILL.md plugins/iasi/skills/writing-plans/results.tsv plugins/iasi/skills/writing-plans/.gitignore && git commit`
  - Change: message 如 `writing-plans: round2 结构去重（MERGE STOP 段独有内容进 PHASE 0 + 删冗余 STOP 段 + 红灯段三段式索引表 + 路由 fork 瘦身）`，正文记：三处同义反复收敛到 PHASE 0 唯一 handler 家（含吸收 L60 路径触发条件 + fork 锚词）、红灯段升级诊断索引表（解 dim3 两段式 + dim7 STOP overlap）、CHECKPOINT 折进 PHASE 6、零行为变更（Task 2 自检通过）、darwin within-judge delta 结论（per-dim 数据入 body）；**MERGE-B 可追溯说明（P1-R1）：PHASE 0 fork 行措辞密度统一——独立 STOP 段 L57-59 的触发情境锚词合并进 L81 既有 fork 行，删 STOP 段前消除两份冗余三选 fork，密度持平、量减**；footer `Co-Authored-By: Claude <noreply@anthropic.com>`。
  - Expected: commit 成功；`git status` clean。
- [ ] Step 2: --no-ff merge 回 main
  - Run: `git checkout main && git merge --no-ff writing-plans-round2`（保留评审脉络）。
  - Expected: merge 成功；main 含 round-2 改动。

## 执行纪律

- 开始实现前先复查整份计划；发现缺项、矛盾或锚点失配先修计划。
- Task 1 内按 Step 编号顺序执行（MERGE 必须先于 DELETE，避免中间态孤儿）；定位一律用章节锚点字符串，行号仅作提示。
- 每个 Step 的"改动后验证"必须实际跑，不要跳过。
- 遇到删除后某条规则找不到存活副本（触发条件或动作任一），立即停下补归属，不要留孤儿。
- darwin 实测禁主 agent 自评，必须 spawn 独立 Agent 子 judge；judge blind（不知 A/B、不知重点 dim、自读 rubric、不给 keep/revert）；只信 within-judge delta。
- results.tsv 一律 Python 追加（禁 printf）；note 单行 `;` 分隔。
- 分支：全程在 `writing-plans-round2`，darwin keep 后才 --no-ff merge main。

## 最终验证

- `wc -l plugins/iasi/skills/writing-plans/SKILL.md` → 约 212–218 行（P2-R1 复算约 214）。
- `grep -nE '^## ' …/SKILL.md` → 无 `🔴 CHECKPOINT / 🛑 STOP 规则`；`红灯与反例` 在（索引表形态）。
- Task 2 的 3 项全 pass（4 条 STOP 触发条件+动作各自 handler 唯一落 PHASE 0、CHECKPOINT 唯一落 PHASE 6、0 外指孤儿、PHASE 0–6 步骤结构未变）。
- Task 3：≥2 独立 judge within-judge delta，dim3/dim7 不降、dim9 hold → keep。
- `python3 -c "import csv;rows=list(csv.reader(open('plugins/iasi/skills/writing-plans/results.tsv'),delimiter='\t'));assert all(len(r)==9 for r in rows);print(len(rows[-1]),'fields last row')"` → 末行 9 列。
- `git log --oneline main -3` → 含 round2 --no-ff merge。

## 审阅 Checkpoint

- 计划正文结束（v3）。请审阅；未获批准不进入实现。
- **darwin baseline 说明（P1-3 修正）**：baseline 即 Task 3 Step 1 的 A 版（HEAD 父提交），Task 3 Step 2 的 same-judge A/B 评分**已自然含基线**（不需要单独跑）。注意 results.tsv 上一条标 PRE-EXISTING 的 67.1 是 **dry_run** 分，与本轮 **full_test** A 版数字不可互换——不要拿 67.1 当 full_test 基线做错误归因。
- 若批准，按 Task 1 → 2 → 3 →（4 条件）→ 5 顺序执行；darwin 结论会在 Task 3 回报。

## 修订记录

**v3 吸收评审第二轮（4 项全收，无回怼）：**
- **P0-R**（v2 自造 redundancy，评审对）：MERGE-A 原把 L60 逐字并入，连带把"或读完后仍无法确定范围"带进新分支，与 PHASE 0 L83-85「范围不明」分支语义重叠。修：Task 1 Step 2 触发条件裁到只剩 L60 独有路径级失败，scope 交还既有分支；放置位置改到「范围不明」分支上方（使"参见下方"指向成立）；Task 2 Step 1 加 P0-R 复验 grep（scope 重叠措辞 0 命中）。对评审给的括号措辞做一处小改良：原"读取最小上下文仍补不上时，按下面...分支处理"略矛盾（STOP 了又叫去别的分支），改成纯边界"参见"措辞。
- **P1-R1**：Task 5 Step 1 commit body 补 MERGE-B 可追溯说明（两份冗余三选 fork 合一、密度持平量减）。
- **P2-R1**：体量复算 MERGE-A 裁后 +2（非 +5），最终约 214；架构快照/体量目标/最终验证同步更新。
- **P2-R2**：Task 3 Step 2 补 darwin judge prompt 模板（只给路径 + 输出表头 + 去 keep/revert + 去 A/B 身份预设）。
- **评审自查撤回**：评审 v1 嘴硬的 L85（实测在 L85 非 L86）、commit footer（实测仓库一律 Claude footer）、L64-73（指 brainstorming 参照成品非 writing-plans）三点，评审第二轮已自查 grep 推翻、撤回。我方 v2 回怼的第 2/3/4 点成立。

**v2 吸收评审 Agent 第一轮报告：**

**已吸收（9 项）：**
- **P0-1**（真坑，评审对）：L60 触发条件在 PHASE 0 无副本 → Task 1 改 MERGE then DELETE，新增 PHASE 0 路径分支承接；Task 2 Step 1 自检口径改"触发条件 + 动作"双验。
- **P0-3**：darwin judge 输出去掉 per-dim keep/revert，改主 agent 跨 judge 整合（Task 3 Step 2/3）；judge blind 不告知重点 dim。
- **P1-1**：删 STOP 段前把 fork 触发情境锚词并入 PHASE 0 fork 行（Task 1 Step 3），保 single-source 全密度。
- **P1-2**：A/B 落 repo-local `.darwin/` + .gitignore；judge 只给路径、自读 rubric、不注入（Task 3 Step 1/2）。
- **P1-3**：baseline 措辞修正——same-judge A/B 自然含基线；dry_run 67.1 ≠ full_test（审阅 Checkpoint）。
- **P1-4**：孤儿扫描加宽正则（Task 2 Step 2），并标注 L85 为合法段内引用。
- **P2-1**：Task 4 加框架冲突判据表（dim7 真退化 / dim3-9 框架冲突 / dim1-2-4-6 噪声）。
- **P2-2**：results.tsv note 单行 `;` 分隔，delta 详情入 commit body（Task 3 Step 4）。
- **P2-3**：全局约束显式声明"不动 test-prompts.json，dim9 预期 hold 不升"。

**回怼（2 项，请转发给评审 Agent）：**
- **P0-2 严重级别夸大 + 2 个事实错误，降级为已吸收的 P1**：
  1. 我计划本就写明"行号仅作当前态提示、用章节锚点定位"（中模型校准约束），行号非承重——够不上 P0。且 v2 已把 Task 2 的承重行号改成锚点引用 + 重跑 grep 锁实测值。
  2. **评审误读了指代**：计划里的"L64-73"指的是**参照成品 brainstorming** 的红灯表（brainstorming 文件内确实在 L64-73 区），不是 writing-plans 的红灯段；writing-plans 红灯段是 L33-42，我从没认错。
  3. **评审自己 off-by-one**：称"按上面的 🛑 STOP 规则"那行在 L86，**实测（grep）在 L85**——我原文 L85 是对的，评审的"修正"反而错了。
  4. 我的 writing-plans 实测行号（STOP 段 L53-63、PHASE 6 L194-210、孤儿行 L85）准确；只有 PHASE 0 handler 区间与 fork 行偏松，v2 已收紧到锚点。
- **P2-4 是伪问题**：实测最近所有 commit（含 `git log -1 e76bbdb`）footer 一律 `Co-Authored-By: Claude <noreply@anthropic.com>`，本仓库无 Copilot convention，我原计划 footer 正确。
