# cleanup skill WGS 优化（结构去重 + 分支收口 + dim7/dim8 open gap 闭合）实施计划

> v3（2026-07-26）：第二轮评审**批准开工**，吸收 4 项非阻塞 polish（全部 grep 复核）。**P1-2 论证修正**：实测 handoff round-2 区间 150–156 实际落 **140** = out-of-band（区间没接住，非 drift）——「区间更诚实」论证歪了，真教训是「行数预测本身不准」；体量目标加警示 + Task 3 加 Step 5「wc 落区间外停下分析」兜底。**P3-2**：Step 7 `grep -cE '反膨胀原则'`→`grep -cE '反膨胀'`（更严格，实测当前仅 L251 一处）；期望 0 的 -cE 保留（期望 0 时 -cE≡-oE\|wc -l，P0-1 bug 只咬非零计数，不矫枉过正）。**P3-3**：开放项 2 ADR 理由补全（段头消失靠核心边界 clause + git history 可恢复，ADR 不必作唯一恢复路径）。**P2-3 评审撤回**：评审撤回合并建议，补一条落地要求——Task 2 三条 prompt 的 expected 措辞区分 L29/L33/L34 具体 disambiguator（执行 Task 2 时落实）。**memory 泛化**：把「CJK 行长度用 python3 len」memory 泛化为「count 工具（grep -c/wc -l/wc -c/awk length）口径 ≠ 语义口径，凡计数/长度断言一律实测」。
>
> v2（2026-07-26）：吸收外部评审 Agent 报告（主 agent 全部 grep 复核，非轻信）。**P0-1**：marker 计数口径 bug——`grep -cE`(行数) ≠ marker 个数（实测 L228 同行 🔴+🛑，行数 4 / 个数 5），全计划改 `grep -oE '🛑|🔴' | wc -l`；同时 Step 3(c) checkpoint 改**单 marker/行**（去掉原 F0 `🔴 CHECKPOINT · 🛑 STOP` 同行双 marker——正是 R2 `ceea669` flagged 的 mild stacking），baseline 5 marker/4 gate → 改后 4 marker/4 gate。**P0-2**：横切 clause 存活检查加双重断言（分层段头 `grep -cE '分层与横切'`=0 + 核心边界段内 `sed -n '/^## 核心边界/,/^## /p'` 含横切），防残留段头假阳性。**P1-1**：Task 4 加「结构盲非身份盲」blind 折扣声明。**P1-2**：体量算术统一 −83 / 约 181 行（区间 175–185）。**P2-1**：立即执行段头 L263→**L261**（off-by-one，L263 是段内文本）+ 加执行前 `grep -nE '^## '` 重抓警示。**P2-2**：开放项 1 理由重构（桥接配方**超出**检索难度轴范畴，非其应用）。**P2-4**：Task 6 Step 0 用词改「首次提交已存在计划」。**P2-3 部分驳回**：governance-soft-vs-hard / rule-explanation-vs-audit 测不要路由**不同 bullet**（L33/L34，现有 #3 测 L29），是 failure-mode 编码广度非冗余，保留 5 条新 prompt，仅澄清覆盖矩阵。
>
> v1（2026-07-26）：基于本会话 `/grill-with-docs` 共识（脊柱 + F3/F4/F6/F7/F8/F9 决策）起草，参照 handoff round-2（`812544a`）/ writing-plans round-2（`98ba477`）走通的 MERGE-before-DELETE + darwin blind A/B 配方。**本轮头号约束（handoff 硬约束#2）：计划写完不自起评审 subagent——v1 单版落盘即停，等用户手动启用外部 agent 评审；修订记录待外部评审后由其驱动追加，非自循环。**

## 目标

- 对本地 `cleanup` skill 做 writing-great-skills 方法论正式优化轮（4 个本地 skill 的最后一个）：**结构去重（脊柱 + F3）+ 分支收口（F6）+ dim7/dim8 open gap 闭合（F3 collapse redundancy / F7 null-handler 补全）+ negation 守卫保留（F8）+ test 补全（F9）**。
- **契约：零行为丢失**。每条被删/被移规则在存活副本里有家；正常 cleanup 流程 PHASE 1-4 的**步骤核**（盘点→判断→整理→输出）不动，只收敛重复表述 + 收口分支 + 闭合 judge-flagged gap。
- 体量目标：264 行 → **约 181 行（净减 ~83，区间 175–185）**（4 个本地 skill 里最长 → 降到 writing-plans/brainstorming 以下、接近 handoff）。明细（**P1-2 统一口径**：各 Step 预期是分量、合计是总量）：删 `分层与横切`(−24) + 删 `触发模型`(−29：36 行删 − 软提醒 7 行并入) + `资格门`并入 PHASE 0(−5) + `强制 cleanup`压成 checkpoint(−20：28 行删 − checkpoint 8 行加) + 删 `反膨胀原则`(−9) + L11 condense(−1)；加 F7 null-handler expand(+3) + 非冗余分工注(+2)；**合计 −83**。**⚠️ 行数预测本身不准**（P3-1/v3）：handoff round-2 区间 150–156 实际落 **140**（out-of-band，区间没接住，非 drift）——区间也未必准，故此区间仅粗估，真兜底靠 Task 3 Step 5「wc 落区间外停下分析」。
- darwin 目标：
  - **dim7（结构/去重）升**——闭合 R3（`dee6e8e`）open gap「redundancy 未 collapse」（judge 当年因分歧 + trigger-core 风险选择不合并，本轮 F3 正面处理）。
  - **dim8（可执行性）升**——闭合 R4（`5c03690`）open gap「null-handler 缺 history-depth spec + no-answer fallback」（F7 补全）。
  - **dim4（视觉检查点）hold**——R2（`ceea669`）的 marker 原在 资格门/F0/F1；F5（资格门并入 PHASE 0）+ F6（强制 cleanup 压成 PHASE 0 checkpoint）**必须把 🔴/🛑 marker 带过去**，否则 dim4 回归。
  - **dim3/dim9（失败模式/反例黑名单）hold**——F8 大部分 negation 是 co-located 微妙守卫保留；dup-negation（反触发/F2）删。框架冲突区（硬约束#11），dim9 可能微降密度，靠不要路由 + 硬约束 L59 + PHASE 0 🛑 桥接。
  - **dim1/dim2（清晰度）预期微升**（sprawl 收缩）。

## 架构快照

- 主干正常 cleanup 流程 PHASE 1-4 步骤核不动。改动集中在：触发/入口模型收口 + 分工二重述合并 + 分支收口 + 反膨胀自指段删除 + null-handler 补全。
- **触发模型收口（脊柱，F1/F2/F5）**：`触发模型`(L89-124) 三部分——`硬触发`(L91-106) ≈ `何时使用`(L14-24) 触发短语逐字重复（硬触发是何时使用的裸短语**子集**）→ DELETE；`软提醒`(L107-116) 是 net-new（何时使用没有）→ MERGE 进 `何时使用`；`反触发`(L117-124) ≈ `不要路由到 cleanup`(L26-37) → DELETE（不要路由作 anti-trigger single source）。`资格门`(L125-137) 的稳定判据 → MERGE 进 `PHASE 0: 验证请求`（PHASE 0 已有「任务已稳定」确认项，资格门是其展开）。"改用 handoff"重定向按轴各留一处：`不要路由`（routing-shape：请求不是 cleanup 形）+ `PHASE 0`（stability：是 cleanup 请求但任务未稳，作强制 checkpoint 的软替代）——**非重复，不同轴**。
- **核心边界吞分层与横切（F3，闭合 dim7 open gap）**：`核心边界`(L39-48) 与 `分层与横切`(L63-87) 是同一套 4-way 分工。核心边界有锋利的「为完成任务改文档 ≠ cleanup vs 为长期知识系统改文档 = cleanup」判据（分层段没有），分层段有「规范审计是横切 ≠ 第四 peer」区别（**R3 counting bug fix 就靠这句**）。合并：核心边界作 base，折入横切 clause 一句，删分层与横切整段。**必须保留横切 clause，否则 dim7 counting bug 回归**。
- **强制 cleanup 压成 PHASE 0 checkpoint（F6）**：`强制 cleanup`(F0/F1/F2, L222-249) 是独立分支（任务未稳却显式要求沉淀）。F0(风险提示)+F1(用户须坚持) 是 silent-drift 微妙守卫（强制 cleanup 正是 silent-drift 高危区），检索难度轴判定须 co-locate 不 disclose → 压成挂 PHASE 0 稳定门失败路径的 checkpoint。F2(强制不写用户记忆) ≈ 硬约束 L54-55 已规定 → DELETE。**checkpoint 必须带 🛑/🔴 marker，否则 dim4 回归**（R2 markers 原在 F0/F1）。
- **反膨胀原则删除（F4）**：`反膨胀原则`(L251-259) 三重述——其 checklist(重复/过期/一次性叙事/错位) ≈ PHASE 2 优先删除表(中间态/一次性/已过期/低价值重复)；其原则 ≈ 硬约束 L52「不做流水账追加器」。DELETE 整段，single source = 硬约束 L52（leading principle）+ PHASE 2（keep/delete 表）。顺带消除讽刺性自指（cleanup 职责是让知识干净，SKILL 自己却最长）。
- **null-handler 补全（F7，闭合 dim8 open gap）**：PHASE 0 裸 `/cleanup` handler(L151-156) R4 judge 标 dim8 cap 8 = 缺 history-depth spec + no-answer fallback。补：history-depth 限定（本次会话 + 仓库最近变更，把「最近」界明确）+ no-answer fallback（用户不答 → 只盘点列候选不写，确认范围再动笔）。
- **negation 大部分保留（F8，框架冲突区）**：按检索难度轴，`不要路由`/硬约束 L57-61/PHASE 各 🛑 守卫都是 co-located 微妙守卫（silent-drift 高危，中模型默认会做错）→ KEEP。dup-negation（反触发/F2）已被脊柱/F6 删。intro L11 身份否定（它不是…也不是…）→ condense 成正面身份。关键守卫加「非冗余」分工注（handoff round-2 N3 同款）防 darwin dim7 误扣。
- **不动**：description frontmatter（路由面敏感，触发短语 invocation source）、references 三件（agent-paths/governance/sync-matrix，runtime-INCLUSIVE 已 PASS 硬约束#13）、PHASE 1/1B/2/3/4 步骤核、GLOSSARY.md / docs/adr（本轮决策不达 ADR 三全门槛——real-tradeoff✓ surprising✓ hard-to-reverse✗；检索难度轴/test-mapped failure mode 已存在并被复用）。

## 全局约束

- **零行为丢失**：每个删除点先确认存活 single source；MERGE 优先于 DELETE——独有 nuance 先并入存活家，再删冗余表述。
- **正常 cleanup PHASE 1-4 步骤核不动**；例外仅：PHASE 0 吸收资格门稳定判据 + 强制 checkpoint + null-handler expand（同区域收敛，步骤核 = 盘点→判断→整理→输出 不变）。
- **dim7/dim4 框架敏感（本轮最高风险）**：F3 必须保留横切 clause（R3 counting fix）；F5/F6 必须把视觉 marker（🛑/🔴）带到 PHASE 0 稳定门 + 强制 checkpoint（R2 dim4 fix）。每个相关 Step 后 grep 验存活。
- **本轮一起补 test-prompts（F9）**：4 → 9 条，覆盖 5 个未测分支。新 prompt 针对新结构设计 → Task 1（SKILL.md 重构）先于 Task 2（test-prompts）。
- **只改 cleanup 一个 skill**：不动 brainstorming / writing-plans / handoff，不动上游冻结的 5 个 skill。
- **中模型校准**：删低密度复述（触发短语讲 3 遍那种），保留高密度锚词；定位用**章节锚点字符串**，行号仅作当前态提示（grep 实测锁定，执行时以锚点为准）。
- **darwin 硬约束**：跨 judge 总分不可比（07-19 的 78.5 是彼时 judge 的分，不可跨 judge 当基线），只信 within-judge delta（blind A/B 同评两版）；judge 不被告知重点 dim、不注入 rubric 正文、不输出 keep/revert（keep/revert 由主 agent 跨 judge 整合）；dim8 实测必须 spawn 独立 Agent 子 judge，禁主 agent 自评；results.tsv 用 Python 追加（9 字段、note 单行 `;` 分隔、assert 无 tab）；结果卡交付 HTML（本 WSL 无 PNG 渲染）。
- **分支**：feature 分支 `cleanup-wgs`，--no-ff merge 回 main。commit footer 沿用仓库惯例 `Co-Authored-By: Claude <noreply@anthropic.com>`。

## 输入工件

- 已批准设计：本会话 `/grill-with-docs` 共识（脊柱 + F3/F4/F6/F7/F8/F9 决策，见上方架构快照）。
- 目标 skill：`plugins/iasi/skills/cleanup/SKILL.md`（当前 264 行）+ `test-prompts.json`（当前 4 条）。
- 形态参照：`plugins/iasi/skills/handoff/SKILL.md`（140 行，round-2 sibling 版式样板：何时使用+不要路由、无独立触发模型段）+ `plugins/iasi/skills/writing-plans/SKILL.md`（220 行）。
- 诊断 rubric：`~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md`。
- 术语/决策上下文：`GLOSSARY.md`（检索难度轴、test-mapped failure mode、中模型校准）、`docs/adr/0001-two-track-design-pull-only-plan-handoff.md`。
- handoff：`docs/handoff/2026-07-26-cleanup-skill-optimization-handoff.md`（13 硬约束）。
- 计划样板：`docs/plans/2026-07-25-handoff-round2-structural-dedup-implementation-plan.md`（含 darwin judge prompt 模板、MERGE-before-DELETE、框架冲突判据表、C2 tie-break）。
- darwin 历史：`plugins/iasi/skills/cleanup/results.tsv`（07-19 baseline 72.3 → R1-R4 后 78.5；**R3 dim7 counting fix + redundancy 未 collapse open gap**、**R4 dim8 null-handler open gap（cap 8 = 缺 history-depth + no-answer fallback）**——本轮 F3/F7 正面闭合这两个 gap）。

## 文件结构与职责

- Modify: `plugins/iasi/skills/cleanup/SKILL.md` — 结构去重 + 分支收口 + dim7/dim8 gap 闭合（Task 1）
- Modify: `plugins/iasi/skills/cleanup/test-prompts.json` — 补全到 9 条（Task 2）
- Modify: `plugins/iasi/skills/cleanup/.gitignore`（新建或追加）— 忽略 `.darwin/` 临时评分文件（Task 4）
- 验证：零行为丢失自检（Task 3，只读）
- darwin 实测：≥2 独立 judge 盲评 A/B（Task 4，只读 + results.tsv 追加）
- 视情况桥接（Task 5，条件触发）
- 收口：feature 分支 commit + --no-ff merge（Task 6）
- **不动**：`references/*.md`、description frontmatter、GLOSSARY.md、docs/adr

## 任务清单

### Task 1: cleanup SKILL.md 重构（结构去重 + 分支收口 + gap 闭合，按区域）

- 目标：按区域收敛重复表述 + 收口分支 + 闭合 dim7/dim8 gap。PHASE 1-4 步骤核不动。
- 涉及文件：`plugins/iasi/skills/cleanup/SKILL.md`
- 为什么是单任务：F5/F6/F7 在 PHASE 0 区域强耦合（资格门并入 + 强制 checkpoint + null-handler expand 都落 PHASE 0）；触发模型/分层/反膨胀虽在不同区域但行号随前序编辑漂移，单任务 + 锚点定位保 diff 连贯、避免跨任务中间态。各区域作 Step 分割，diff 可读。编辑按**章节锚点字符串**定位（非行号）。
- 接口契约
  - Consumes：已批准设计（脊柱 + F3/F4/F6/F7/F8）
  - Produces：重构后 SKILL.md（PHASE 1-4 步骤核原样；触发模型删 + 软提醒并入何时使用；资格门并入 PHASE 0；强制 cleanup 压成 PHASE 0 checkpoint；分层与横切并入核心边界保横切 clause；反膨胀删；null-handler 补全；L11 condense；非冗余分工注）
- 验证范围：行数落到约 181（区间 175–185）；存活副本 grep 验每个删除点；dim7 横切 clause 存活；dim4 marker 存活。

- [ ] Step 1: 改动前检查（基线快照）
  - Run: `cd plugins/iasi/skills/cleanup && wc -l SKILL.md && grep -nE '^## |^### ' SKILL.md`
  - Expected: 264 行；章节含 `## 何时使用`(L14)、`## 不要路由到 cleanup`(L26)、`## 核心边界`(L39)、`## 硬约束`(L50)、`## 分层与横切`(L63)、`## 触发模型`(L89)、`## 资格门`(L125)、`### PHASE 0: 验证请求`(L141)、`## 强制 cleanup`(L222)、`## 反膨胀原则`(L251)、`## 立即执行`(L261)。记录为比对基线。

- [ ] Step 2: 脊柱——删触发模型，软提醒并入何时使用（F1 + F2）
  - 锚点：`## 触发模型`(L89) 到 `## 资格门`(L125) 之前。
  - Change（**先 MERGE 后 DELETE，每步 grep 验存活，避免中间态孤儿**）：
    - **(a) MERGE 软提醒进何时使用**：`## 何时使用` 段末（L24「仅因为…不足以自动进入 cleanup」之后）追加软提醒子节——「**软提醒**：语义出现"阶段完成、适合沉淀"信号（`这个阶段做完了` / `可以交给别人了` / `新人能直接上手了` / `准备收尾`）时，不自动执行 cleanup，只提示用户现在适合做一次。」（吸收 `### 软提醒` L107-116 全部内容 + 典型表达）。
    - **(b) DELETE 触发模型整段**（L89-124）：`### 硬触发`(L91-106) ≈ 何时使用触发短语子集 → 删（何时使用是 single source，触发短语 invocation source 在 description）；`### 软提醒` 已 (a) 并入；`### 反触发`(L117-124) ≈ 不要路由到 cleanup → 删（不要路由是 anti-trigger single source）。
  - 理由：硬触发是何时使用的裸短语子集（逐字重复），反触发与不要路由重复；软提醒是 net-new 并入何时使用。三重触发短语（description + 何时使用 + 硬触发）降为两重（description + 何时使用）。
  - 预期：约 −29 行（触发模型 36 行删，软提醒 ~7 行并入何时使用 net +0）。

- [ ] Step 3: PHASE 0 区域——资格门并入 + null-handler 补全 + 强制 cleanup 压成 checkpoint（F5/脊柱 + F7 + F6）
  - 锚点：`## 资格门`(L125-137) + `### PHASE 0: 验证请求`(L141-156) + `## 强制 cleanup`(L222-249)。
  - Change（子顺序，每步 grep 验存活）：
    - **(a) MERGE 资格门稳定判据进 PHASE 0**：PHASE 0 的确认项「当前任务已经足够稳定，适合写入长期知识」展开吸收资格门 4 条件（核心目标已完成或停在稳定可交接终点 / 不再依赖下一轮探索决定主要结论 / 已有正式工件足以承载稳定事实 / 不会把中间态判断写死）+ 资格门的审计额外要求（审计范围明确、主要对象能机械核验）+ 🛑 gate（不满足 → 告知任务未稳，或改用 `handoff`）。**DELETE `## 资格门` 整段**（L125-137）。
    - **(b) F7 null-handler expand**：PHASE 0 裸 `/cleanup` handler（L151-156）补两件——**history-depth 限定**（把「最近会话和仓库最近变更」明确为「本次会话 + 最近提交 + 当前工作区改动 + 刚稳定的文件」，给「最近」一个可执行界）；**no-answer fallback**（「如果问完一两个问题用户仍不明确范围，默认只盘点、列候选、不写文件，等用户确认范围后再动笔」）。
    - **(c) F6 强制 cleanup 压成 PHASE 0 checkpoint**：PHASE 0 稳定门之后加强制 checkpoint，**每个决策点单独一行、单 marker**（**P0-1 修正**：去掉原 F0 `🔴 CHECKPOINT · 🛑 STOP` 同行双 marker——那是 R2 `ceea669` judge 点名的 mild stacking；合并是顺手清理它的机会）：
      - 🔴 **CHECKPOINT**（稳定门不过 + 用户显式强制）：先告知（当前任务仍处中间态 / 直接沉淀可能污染长期知识 / 若只想切到下一 chat 继续做宜用 `handoff`）；
      - 🛑 只有用户看过上述风险仍明确坚持，才继续（否则停在告知，不自行推进）；继续时写入边界仍守硬约束（仓库内优先，用户记忆须用户再次明确要求才写）。
      **marker 计（P0-1 口径）**：硬约束🔴 + 稳定门🛑 + checkpoint🔴 + checkpoint🛑 = **4 marker / 4 gate**（baseline 5 marker/4 gate，合并去掉 F0 同行多出的那个 🛑 = R2 flagged 的 stacking，gate 数 4→4 不降）。**DELETE `## 强制 cleanup` 整段**（L222-249，F0/F1/F2）：F0+F1 语义进 checkpoint，F2（强制不写用户记忆）≈ 硬约束 L54-55 已规定 → 删。**同步**：`## 立即执行` 段（**段头 L261**；L263 是段内首行文本——P2-1 修正 off-by-one）「先判断这次请求应该走 `handoff`、正常 cleanup 还是强制 cleanup」改为两段路由「走 `handoff` 还是 cleanup；若进 cleanup 但任务未稳，PHASE 0 稳定门与强制 checkpoint 会处理」（强制 checkpoint 作 PHASE 0 内子路径，不当 peer 路由选项）。
  - 理由：资格门是 PHASE 0 稳定判据的展开，并入消除 gate 二重述；F7 闭合 R4 dim8 open gap；F6 把强制分支收口到稳定门失败路径（silent-drift 守卫 co-locate 不 disclose），F2 与硬约束重复。
  - **dim4 风险（R2 markers）**：(a) PHASE 0 稳定门带 🛑 + (c) 强制 checkpoint 带 🔴(风险)+🛑(坚持门)，保 dim4 gate 密度（R2 原在资格门/F0/F1 的 4 gate 迁到 硬约束 + PHASE 0 稳定门 + checkpoint 风险/坚持 = 4 gate）。**marker 口径见 P0-1**：用 `grep -oE|wc -l` 数个数（4），非 `grep -cE` 行数。
  - 预期：资格门 −13（并入 PHASE 0 ~+8 net −5）+ null-handler +3 + 强制 cleanup −28（checkpoint ~+8 net −20）+ 立即执行措辞 0 行变化 ≈ net −22。

- [ ] Step 4: 核心边界吞分层与横切（F3，闭合 dim7 open gap）
  - 锚点：`## 核心边界`(L39-48) + `## 分层与横切`(L63-87)。
  - Change:
    - **MERGE 横切 clause 进核心边界**：核心边界第 4 bullet「规范审计负责"规则是否被实践遵守"的可核验部分，不负责替代代码审查或架构设计」改为「规范审计是**横切层**（不是第四个 peer 层），负责"规则是否被实践遵守"的可核验部分，不替代代码审查或架构设计」——吸收 `### 4. 规范执行横切层`(L83-87) 的 load-bearing 区别（**R3 counting fix 靠它**：分层与横切 = 3 层 + 1 横切，不是 4 个 peer）。
    - **DELETE `## 分层与横切` 整段**（L63-87）：前 3 节（`### 1. 会话连续性层` / `### 2. 正式工件层` / `### 3. 长期知识层`）= 核心边界前 3 bullet 的展开（面向/包括自明，无独有 nuance）→ 删。核心边界的「同样是改文档：为完成任务而改 ≠ cleanup / 为长期知识系统而改 = cleanup」判据（分层段没有）保留。
  - 理由：核心边界与分层与横切是同一套 4-way 分工；核心边界有「改文档 ≠ cleanup」锋利判据 + 压缩，吞分层与横切；横切 clause 必须保留否则 dim7 counting bug 回归（R3）。
  - **dim7 风险（R3 counting fix）**：横切 clause（「不是第四 peer」）是 R3 `dee6e8e` 修的 counting bug 关键，merge 后必须留在核心边界。
  - 预期：约 −24 行（分层与横切 25 行删，横切 clause ~1 行并入核心边界 net −24）。

- [ ] Step 5: 删反膨胀原则 + intro L11 condense（F4 + F8）
  - 锚点：`## 反膨胀原则`(L251-259) + intro L11。
  - Change:
    - **DELETE `## 反膨胀原则` 整段**（L251-259）：checklist（有没有重复条目 / 过期说明 / 一次性叙事塞进长期规则 / 本该在正式工件的堆进长期知识）≈ PHASE 2「优先删除或避免写入」（中间态判断 / 一次性叙事 / 已过期事实 / 低价值重复信息）；原则 ≈ 硬约束 L52「优先编辑和清理现有知识，不要把 cleanup 做成流水账追加器」。single source = 硬约束 L52（leading principle）+ PHASE 2（keep/delete 表）。
    - **L11 condense**：「它不是中途交接工具，也不是普通总结工具，也不替代代码评审。」→ DELETE（身份否定，不要路由段已覆盖路由 disambiguation；intro 第一句「把已经稳定下来的任务结论，整理成可长期复用的仓库内知识」已是正面身份，第二句「它的职责是做终态的知识清理…」已划边界）。
  - 理由：反膨胀三重述 + 自指讽刺；L11 身份否定是 no-op（不要路由段 single source）。
  - 预期：约 −10 行（反膨胀 9 + L11 1）。

- [ ] Step 6: 关键守卫「非冗余」分工注（F8，防 dim7 误扣）
  - 锚点：`## 不要路由到 cleanup` + `## 硬约束`。
  - Change: 给可能被 darwin dim7 误判冗余的守卫加分工注（handoff round-2 N3 同款）——
    - `不要路由到 cleanup` 段首加一句：「（routing 判别——请求是否 cleanup 形；与硬约束的执行纪律不同轴，非重复）」。
    - 硬约束 L59「做规范审计时…不要把具体规则复制进 cleanup，只现场读取规则」加一句：「（governance 审计纪律——规则真身现场读，与不要路由的请求判别不同轴，非重复）」。
  - 理由：F8 大部分 negation 保留，但 darwin dim7 可能把「不要路由 vs 硬约束 negation」判冗余；分工注显式声明不同轴，防误扣。
  - 预期：约 +2 行。

- [ ] Step 7: 改动后验证
  - Run: `wc -l SKILL.md`（期望约 181，区间 175–185）&& `grep -nE '^## ' SKILL.md`（期望：**无** `触发模型` / `分层与横切` / `资格门` / `强制 cleanup` / `反膨胀原则`；**有** `何时使用` / `不要路由到 cleanup` / `核心边界` / `硬约束` / `正常 cleanup 流程` / `立即执行`）&& `grep -cE '硬触发|反触发' SKILL.md`（期望 0）&& `grep -cE '分层与横切' SKILL.md`（期望 0）&& `grep -cE '反膨胀' SKILL.md`（期望 0，**P3-2**：查所有"反膨胀"出现不只"反膨胀原则"短语，更严格；实测当前仅 L251 一处。注：期望 0 的 -cE 保留不变——期望 0 时 -cE ≡ -oE\|wc -l，P0-1 口径 bug 只咬非零计数，不矫枉过正）&& `grep -nE '横切' SKILL.md`（期望命中核心边界段，dim7 fix 存活——严格双重断言见 Task 3 Step 2）&& `grep -oE '🛑|🔴' SKILL.md | wc -l`（**期望 4**，dim4 fix 存活——**P0-1 口径**：用 marker 个数非行数；baseline 实测 **5 marker/4 gate**（L228 同行 🔴+🛑 各算 1），改后 **4 marker/4 gate**：硬约束待拍板🔴 + PHASE0 稳定门🛑 + 强制 checkpoint🔴 + 强制 checkpoint🛑，单 marker/行）&& 存活副本 + 孤儿扫描（见 Task 3）。
  - Expected: 行数达标；删段消失；横切 clause + marker 存活；PHASE 1/1B/2/3/4 步骤核零改动（diff 增删仅落在 Step 2-6 位点）。

### Task 2: test-prompts 补全（4 → 9 条，F9）

- 目标：补 test-prompts 覆盖 5 个未测分支，使 darwin 评估与回归有足够触点。
- 涉及文件：`plugins/iasi/skills/cleanup/test-prompts.json`
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md（新 prompt 针对新结构设计）
  - Produces：9 条 test-prompts（含 expected）+ 覆盖矩阵
- 验证范围：JSON 合法；每条 prompt 映射到一个 PHASE/守卫；覆盖矩阵无盲区。

- [ ] Step 1: 新增 5 条 prompt（保留现有 4 条；现有 id 实测为 1-4 连续，新 id 从 5 起）
  - Change: 追加——
    - `forced-cleanup-checkpoint`：任务未稳定（功能还在做、核心目标未达成）+ 用户显式要求 cleanup → 测 PHASE 0 强制 checkpoint（F6）：先告知风险（中间态/污染长期知识/宜用 handoff）+ 用户须坚持 + 写入边界守硬约束。（测 F6）
    - `governance-soft-vs-hard`：用户说「审计下代码质量 / 找安全漏洞 / 查 PR 风险」 → 不路由到 cleanup governance 审计（代码质量审 ≠ 仓库规则审），测 `不要路由` L33 disambiguator。
    - `anti-bloat-dedup`：仓库 AGENTS.md 已有过期叙事 + 重复条目 + 一次性流水账 → 测 PHASE 2 优先删除 + PHASE 3「删旧优于追加 / 合并优于堆叠」（F4 single source）。
    - `plugin-published-surface`：插件仓库里一个 skill 改名了 → 测 sync-matrix（README 清单 + manifest + marketplace metadata + CHANGELOG 同步面）。
    - `rule-explanation-vs-audit`：用户问「这条规则怎么理解」但没要求核对实践 → 不进 governance 审计，测 `不要路由` L34 meta 守卫。
  - Expected: JSON 合法，9 条，每条有 prompt + expected。

- [ ] Step 2: 覆盖矩阵（映射 prompt → PHASE/守卫）
  - 验证：下列映射无盲区——
    | prompt | 覆盖 |
    |---|---|
    | 现有 1 happy-path 沉淀 | PHASE 0-4 正常流 |
    | 现有 2 规范审计 | PHASE 1B governance |
    | 现有 3 反触发/资格门 | 不要路由 **L29**（handoff-shape 路由）+ 稳定门（F5 后在 PHASE 0） |
    | 现有 4 null 裸调用 | PHASE 0 null-handler（F7 expand 后：history-depth + no-answer fallback） |
    | 新 forced-cleanup-checkpoint | PHASE 0 强制 checkpoint（F6） |
    | 新 governance-soft-vs-hard | 不要路由 L33（代码质量审 ≠ 规则审） |
    | 新 anti-bloat-dedup | PHASE 2/3（F4） |
    | 新 plugin-published-surface | sync-matrix（references） |
    | 新 rule-explanation-vs-audit | 不要路由 L34（解释 ≠ 审计） |
  - Expected: F3/F4/F6/F7 改动面 + 5 未测分支均有 prompt 覆盖；dim3/dim9（failure mode 编码）有 ≥4 条 routing/guard prompt 支撑。
  - **注（P2-3 澄清，部分驳回评审建议）**：现有 #3 测不要路由 **L29**（handoff-shape 路由），新 `governance-soft-vs-hard` 测 **L33**（代码质量审 ≠ 规则审），新 `rule-explanation-vs-audit` 测 **L34**（解释 ≠ 审计）——三条测不要路由的**不同 bullet**（L29/L33/L34），是 failure-mode 编码**广度**非冗余（dim3/dim9 奖励多失败模式显式编码）；边界清晰（三种不同 disambiguator 场景），**保留 5 条新 prompt 不合并**。仅澄清矩阵 bullet 标注。

### Task 3: 零行为丢失自检（只读）

- 目标：实证「零行为丢失」，**同时验触发条件 + 动作**有存活 single source；并验 dim7/dim4 框架 fix 在压缩后存活。
- 涉及文件：只读 Task 1 产物
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md
  - Produces：自检结论（pass / 需补归属）
- 验证范围：下列 4 项全部通过。

- [ ] Step 1: 被删规则存活副本检查（触发条件 + 动作，位置敏感）
  - Run:
    - 触发短语：`grep -nE '做最终沉淀|更新长期知识|整理长期记忆|检查规范|审计规则|audit the rules' SKILL.md` → 期望只在 `何时使用` + description 出现，`硬触发` 段 0 残留。
    - 软提醒信号：`grep -nE '阶段做完了|可以交给别人了|新人能直接上手了|准备收尾' SKILL.md` → 期望命中 `何时使用` 软提醒子节。
    - 反触发：`grep -nE '新开 chat 接着做|交接到下一轮|继续当前任务|review 这段代码|找一下 bug' SKILL.md` → 期望只在 `不要路由到 cleanup` 段（`反触发` 独立段已删）。
    - 资格门稳定判据：`grep -nE '核心目标已经完成|不再依赖下一轮|正式工件足以|中间态判断写死' SKILL.md` → 期望命中 PHASE 0 稳定门（`资格门` 段已删）。
    - 强制 cleanup F0/F1：`grep -nE '中间态|污染长期知识|坚持' SKILL.md` → 期望命中 PHASE 0 强制 checkpoint（F0/F1 独立段已删）。
    - F2 用户记忆边界：`grep -nE '用户记忆' SKILL.md` → 期望命中硬约束 L54-55（F2 删后存活）。
    - 反膨胀 checklist：`grep -nE '重复条目|过期|一次性叙事' SKILL.md` → 期望命中 PHASE 2 优先删除表（`反膨胀原则` 段已删）。
    - 分层与横切 4 层：`grep -nE '会话连续性层|正式工件层|长期知识层|规范执行横切层' SKILL.md` → 期望独立段 0 残留；横切语义命中核心边界。
  - Expected: 每个删除点的触发条件 + 动作有存活 single source；无孤儿。

- [ ] Step 2: dim7/dim4 框架 fix 存活检查
  - Run:
    - **横切 clause（R3 dim7 fix，P0-2 双重断言）**：
      - 残留段头：`grep -cE '分层与横切' SKILL.md` → 期望 **0**（防「只删正文小节、留下 `## 分层与横切` 段头」导致 `grep 横切` 假阳性——实测当前 `横切` 命中 L63 段头 + L83 子节，删段后段头必须一并清除）。
      - clause 落点：`sed -n '/^## 核心边界/,/^## /p' SKILL.md | grep -c '横切'` → 期望 **≥1**（横切 clause 必须落在核心边界**段内**，含「规范审计是横切层（不是第四个 peer）」——R3 counting fix 的关键）。
    - **视觉 marker（R2 dim4 fix，P0-1 口径）**：`grep -oE '🛑|🔴' SKILL.md | wc -l` → 期望 **4**（用 marker 个数非行数；baseline 5 marker/4 gate——L228 同行 🔴+🛑 各算 1；改后 4 marker/4 gate，checkpoint 单 marker/行，去掉 F0 同行多余 🛑）。dim4 gate 密度 4→4 不降。
  - Expected: dim7 counting fix + dim4 marker fix 在压缩后存活。

- [ ] Step 3: 孤儿指针扫描（区分 section 引用 vs 行为引用）
  - Run A（section 引用，期望全删）: `grep -nE '触发模型|分层与横切|资格门|反膨胀原则|PHASE F0|PHASE F1|PHASE F2' SKILL.md` → 期望 **0 命中**（这几个只作段头/段内引用，无跨段行为引用）。
  - Run B（强制 cleanup，**不能期望 0**——区分行为引用 vs 路由孤儿）: `grep -nE '强制 cleanup' SKILL.md` → 期望 **2 命中且都是行为引用**：description(L3)「强制 cleanup 也不默认写入用户记忆」+ 硬约束(L55)「强制 cleanup 也不改变上面的默认边界」——这两条是 forced 场景的**写入边界行为约束**，F6 后仍成立（checkpoint 写入边界守硬约束），**保留不动**。`## 立即执行`(L263) 原「走 handoff、正常 cleanup 还是强制 cleanup」须已在 Step 3(c) 改为两段路由（handoff vs cleanup，强制 checkpoint 作 PHASE 0 内子路径，不当 peer 路由选项）——即 L263 不再出现「强制 cleanup」作独立路由目的。

- [ ] Step 4: PHASE 1-4 步骤核未变检查
  - Run: `git diff -- plugins/iasi/skills/cleanup/SKILL.md`，逐 hunk 核对——增删行须全部落在 Step 2（触发模型）/ Step 3（PHASE 0 区域）/ Step 4（核心边界+分层）/ Step 5（反膨胀+L11）/ Step 6（分工注）位点。PHASE 1/1B/2/3/4 步骤核、references 指针零改动。
  - Expected: 主干步骤核无改动；diff 可追溯到 Step 2-6。

- [ ] Step 5: wc -l 落区间外兜底（P3-1/v3）
  - Run: `wc -l SKILL.md`
  - Expected: 若落在 175–185 区间内，直接进 Task 4。**若 < 170 或 > 190（out-of-band），停下分析**哪一项分量超/不足预期（哪个 Step 删多了/少了）——handoff round-2 教训：区间 150–156 实际落 140，行数预测本身不准，**不要默默接受**一个落在区间外的结果而不解释。分析后或修正预期、或回查是否删多了 load-bearing 内容，再进 Task 4。

### Task 4: darwin full_test 实测（blind A/B）

- 目标：用独立 judge 盲评改后(B) vs 改前(A)，within-judge delta 验证 dim7 升（collapse redundancy）、dim8 升（null-handler 补全）、dim4 hold（marker 存活）、dim3/dim9 hold（negation 保留）、dim1/dim2 微升。
- 涉及文件：只读 SKILL.md（A/B 两版落 `.darwin/`）；追加 `results.tsv`
- 接口契约
  - Consumes：Task 1–3 通过 + Task 2 新 test-prompts
  - Produces：≥2 judge 的 per-dim 双分数 + Δ；results.tsv 新行
- 验证范围：≥2 独立 Agent 子 judge；每个 judge 同评 A/B 两版；judge 不被告知重点 dim、不注入 rubric、不输出 keep/revert。

- [ ] Step 1: 落 A/B 两版到 repo-local 临时文件
  - Run:
    - `mkdir -p plugins/iasi/skills/cleanup/.darwin`
    - A 版：`git show HEAD:plugins/iasi/skills/cleanup/SKILL.md > plugins/iasi/skills/cleanup/.darwin/cl_A.md`（改前 264 行 post-R4 版）
    - B 版：`cp plugins/iasi/skills/cleanup/SKILL.md plugins/iasi/skills/cleanup/.darwin/cl_B.md`（Task 1 产物）
    - 确保 `.darwin/` 在 `.gitignore`（新建或追加一行 `.darwin/`）；不用裸 `/tmp`（WSL sandbox TMPDIR 风险）。
  - Expected: 两版文件就绪；`.darwin/` 不入 git。

- [ ] Step 2: spawn ≥2 独立 judge（Agent 工具，独立 context，blind）
  - Run: 每个 judge 的 prompt **只给两个文件路径** `cl_A.md` / `cl_B.md`，**不告诉哪个是改前/改后、不点名重点 dim、不注入 darwin rubric 正文**（让 judge 自己读 `~/.claude/skills/darwin-skill/SKILL.md` 的 9-dim rubric）。要求每个 judge 按 9-dim 全评两版，输出**每维 A_score、B_score、Δ(B−A)**，**不要给 keep/revert 结论**。
  - prompt 模板（spawn 时照填，只换 judge 编号；**用绝对路径**——子 judge cwd 不保证在 repo root）：
    ```
    读取以下两份 SKILL.md（标记 A 和 B，身份未知，不要假设哪个是改前/改后）：
      A: /home/iasi/workspace/m/plugins/iasi/skills/cleanup/.darwin/cl_A.md
      B: /home/iasi/workspace/m/plugins/iasi/skills/cleanup/.darwin/cl_B.md
    按 /home/iasi/.claude/skills/darwin-skill/SKILL.md 描述的 9-dim rubric（dim1-dim9）各评两版，
    输出 markdown 表格：| dim | A_score | B_score | Δ(B−A) | 简评 |
    不要给 keep/revert 结论；不要预设重点 dim。
    ```
  - 硬约束：禁主 agent 自评（darwin 反例 #1）；judge 盲评不知 A/B 身份；keep/revert 不在 judge 做。
  - Expected: ≥2 份独立 per-dim 双分数 + Δ。

- [ ] Step 3: 主 agent 跨 judge 整合 keep/revert
  - **blind 折扣声明（P1-1）**：A 版 264 行 / B 版 ~181 行，章节结构差异大（B 无 `触发模型`/`分层与横切`/`资格门`/`强制 cleanup`/`反膨胀原则`）。judge 第一眼对比结构即可推断「B 是更精简版 = 改后」——blind 是**结构盲非身份盲**。这是 darwin 跨版本盲评的固有极限（handoff / writing-plans round-2 同款，非本轮独有）：within-judge delta 仍可信（同一 judge 对 A/B 同 bias，delta 抵消身份推断），但 judge 对「B 更好」的**绝对倾向**可能受身份推断轻微影响——结论里**不过度宣称 blind 干净**，只报告 within-judge delta。
  - Run: 主 agent 汇总 ≥2 judge 的 per-dim Δ，看方向一致性。重点 dim（由主 agent 事后识别，judge 不知情）判据：
    - **dim7**（直接对应 collapse redundancy）：预期升（闭合 R3 gap）；Δ 不显著为负（> −1）即 keep，若显著为负 = 横切 clause 丢了/留孤儿 → 回 Task 1 Step 4 补。
    - **dim8**（直接对应 null-handler）：预期升（闭合 R4 gap）；Δ 不显著为负即 keep，若显著为负 → 回 Task 1 Step 3(b) 补 history-depth/fallback。
    - **dim4**（R2 已修，F5/F6 带 marker）：Δ > −1 即 keep；若显著为负 = marker 丢了 → 回 Task 1 补 marker。
    - **dim3/dim9**（框架冲突区，F8 保留 negation）：Δ > −1 即 keep；**dim9 预期可能微降（dup-negation 删致密度降，Δ −1 ~ −2 可接受，框架冲突区）——Δ 在 −2 以内且 ≥2 judge 方向一致判属「框架冲突可接受」即 keep**。
    - dim1/2/5/6（间接）：若降 = judge 噪声/方差；除非 ≥2 judge 一致，否则 disregard。
    - **Tie-break（C2）**：若 2 judge 在某重点 dim 方向相反（一正一负），spawn 第 3 个独立 judge（同 blind 协议），按多数方向判——本轮涉 F3 collapse + F8 negation 保留，dim7/dim9 方差可能比 R1 大，预设此规则防僵局。
  - Expected: 给出 keep / 触发 Task 5 的整合结论 + 依据。

- [ ] Step 4: 追加 results.tsv（Python，9 字段，note 单行）
  - Run: Python 追加一行，字段 = `timestamp \t commit \t cleanup \t old_score \t new_score \t status \t dimension \t note \t eval_mode`；每字段 `assert '\t' not in f`；note **单行**用 `;` 分隔多段（禁换行/tab）；`write('\n'.join(lines)+'\n')`；末行列数 = 9。
  - note 记录：`WGS优化(触发模型删+软提醒并入何时使用+资格门并入PHASE0+分层并入核心边界保横切clause+强制cleanup压PHASE0checkpoint+反膨胀删+null-handler补history-depth+no-answer fallback+negation大部分保留+L11condense+非冗余分工注)+test补全4→9; dim7 collapse redundancy闭合R3 gap / dim8 null-handler闭合R4 gap / dim4 marker存活; within-judge delta per dim 见 commit body; 判定 X; 独立judge盲评full_test; 若C2 tie-break fired 追加 'tie-break: dim X 方向相反 spawn j3'`。delta 详细数据写 commit message body（不入 tsv）。
  - Expected: results.tsv 合法追加，9 列，note 单行。

### Task 5: 视情况桥接（条件触发，附框架冲突判据表）

- 目标：若 darwin 出现任一重点 dim 的 within-judge delta 显著为负且整合判 revert，用 co-located 守卫 + 诊断索引表桥接后再复测。
- 触发条件：Task 4 Step 3 整合判定 revert（≥2 judge 同一重点 dim 方向一致显著为负）。
- 涉及文件：视情况 Modify SKILL.md + 复测
- 接口契约
  - Consumes：Task 4 delta 信号
  - Produces：桥接版（若触发）+ 复测 delta
- 验证范围：若触发，桥接后再跑 Task 4 Step 2 复测，within-judge delta 转正或 hold。

- [ ] Step 1: 诊断负 delta（框架冲突判据表）
  - 判据：
    | 负 delta 的 dim | 与本轮改动关系 | 判定 |
    |---|---|---|
    | dim7（结构/整体架构） | 直接对应（collapse redundancy） | 预期升；若降 = **真退化**（横切 clause 丢了/留孤儿）→ 回 Task 1 Step 4 补横切 clause |
    | dim8（可执行性） | 直接对应（null-handler） | 预期升；若降 = **真退化** → 回 Task 1 Step 3(b) 补 history-depth/fallback |
    | dim4（视觉检查点） | R2 已修，F5/F6 带 marker | 若降 = marker 丢了 → 回 Task 1 补 marker |
    | dim3/dim9（失败模式/反例黑名单） | 框架冲突区（F8 保留 negation，dup-negation 删） | 若降 = **框架冲突**（多半来自删反触发/F2 致密度降）→ 走 Step 2 桥接 |
    | dim1/2/5/6（与去重间接相关） | 间接 | 若降 = judge 噪声/方差；除非 ≥2 judge 一致，否则 disregard |
  - Expected: 区分真退化 / 框架冲突 / 噪声；真退化回 Task 1 对应 Step，框架冲突走 Step 2，噪声 disregard。

- [ ] Step 2: 桥接（仅框架冲突）
  - Change: 若 dim3/dim9 因删 dup-negation（反触发/F2）显著降，用「保留/强化 co-located 守卫（不要路由段 + 硬约束 L59 governance 纪律 + PHASE 0 🛑）作真正处理器」桥接（参照 brainstorming `5f54f04` / writing-plans round-2 / handoff round-2 N3 桥接配方）。回退首选：确认 `不要路由到 cleanup` 的 anti-trigger 黑名单密度足够（dim9 奖励显式编码），必要时把反例补详（而非回退 L11——L11 是 no-op 身份否定，回退收益低）。若 dim7/dim8/dim4 真退化，回 Task 1 对应 Step 补（不是框架冲突）。
  - Expected: 桥接版就绪，复测 delta 转正/hold。

### Task 6: 收口（feature 分支 + commit + --no-ff merge）

- 目标：在 `cleanup-wgs` 分支收口，--no-ff merge 回 main。
- 涉及文件：SKILL.md + test-prompts.json + results.tsv（+ .gitignore + 本计划文档）
- 接口契约
  - Consumes：Task 1–5 全通过（darwin keep）
  - Produces：feature 分支 commit + main 上 --no-ff merge
- 验证范围：commit message 说明去重 + 分支收口 + dim7/dim8 gap 闭合 + 零行为变更 + darwin delta；merge 保留评审脉络。

- [ ] Step 0: 分支与计划文档归属
  - Change: 建分支并**首次提交已存在的计划文件**（P2-4 修正用词——本计划文件已在工作区未提交，非新建，勿在新分支重新生成覆盖）：`git checkout -b cleanup-wgs`（未提交的计划文件随 checkout 带到新分支）→ `git add docs/plans/2026-07-26-cleanup-skill-wgs-optimization-implementation-plan.md && git commit -m "docs(plans): cleanup skill WGS 优化实施计划"`。
- [ ] Step 1: 暂存与提交（工作改动）
  - Run: `git add plugins/iasi/skills/cleanup/SKILL.md plugins/iasi/skills/cleanup/test-prompts.json plugins/iasi/skills/cleanup/results.tsv plugins/iasi/skills/cleanup/.gitignore && git commit`
  - Change: message 如 `cleanup: WGS 结构去重+分支收口+dim7/dim8 gap 闭合（触发模型删+软提醒并入何时使用+资格门并入PHASE0+分层并入核心边界保横切clause+强制cleanup压PHASE0checkpoint+反膨胀删+null-handler补全+negation保留+test补全4→9）`，正文记：触发模型三部分收口（硬触发 dup 删 / 软提醒并入何时使用 / 反触发 dup 删）、资格门并入 PHASE 0 稳定门、分层与横切并入核心边界（保横切 clause，闭合 R3 dim7 gap）、强制 cleanup F0/F1 压成 PHASE 0 强制 checkpoint（F2 删，marker 保 dim4）、反膨胀原则删（single source 硬约束 L52 + PHASE 2）、null-handler 补 history-depth + no-answer fallback（闭合 R4 dim8 gap）、negation 大部分保留 + L11 condense + 非冗余分工注、test-prompts 4→9、零行为变更（Task 3 自检通过）、darwin within-judge delta 结论（per-dim 数据入 body）；footer `Co-Authored-By: Claude <noreply@anthropic.com>`。
  - Expected: commit 成功；`git status` clean。
- [ ] Step 2: --no-ff merge 回 main
  - Run: `git checkout main && git merge --no-ff cleanup-wgs`（保留评审脉络）。
  - Expected: merge 成功；main 含本轮改动。

## 执行纪律

- 开始实现前先批判性复查整份计划 **+ 外部评审意见**；发现缺项、矛盾、命名不一致或锚点失配先修计划。
- Task 1 内按 Step 编号顺序执行（MERGE 必须先于 DELETE，避免中间态孤儿）；定位一律用章节锚点字符串，**行号仅作 v1 草拟态快照——每个 Step 执行前先 `grep -nE '^## '` 重抓当前行号**（P2-1：前序编辑会使行号漂移；已发现一处 off-by-one：`## 立即执行` 段头是 L261，L263 是段内首行文本）。
- 每个 Step 的「改动后验证」必须实际跑，不要跳过。
- 遇到删除后某条规则找不到存活副本（触发条件或动作任一），立即停下补归属，不要留孤儿。
- **dim7 横切 clause + dim4 marker 是本轮最高风险点**——F3/F5/F6 必须保活，每个相关 Step 后 grep 验（横切命中核心边界 / 🛑🔴 计数不降）。
- darwin 实测禁主 agent 自评，必须 spawn 独立 Agent 子 judge；judge blind（不知 A/B、不知重点 dim、自读 rubric、不给 keep/revert）；只信 within-judge delta。
- results.tsv 一律 Python 追加（禁 printf）；note 单行 `;` 分隔。
- 分支：全程在 `cleanup-wgs`，darwin keep 后才 --no-ff merge main。

## 最终验证

- `wc -l plugins/iasi/skills/cleanup/SKILL.md` → 约 181 行（净减 ~83，区间 175–185）。
- `grep -nE '^## ' …/SKILL.md` → 章节齐全；无 `触发模型`、无 `分层与横切`、无 `资格门`、无 `强制 cleanup`、无 `反膨胀原则`。
- Task 3 的 4 项全 pass（触发短语/软提醒/反触发/资格门/强制/F2/反膨胀/分层 各有存活 single source；横切 clause 存活；marker 存活；0 外指孤儿；PHASE 1-4 步骤核未变）。
- `python3 -c "import json;json.load(open('plugins/iasi/skills/cleanup/test-prompts.json'));print('json ok')"` → JSON 合法，9 条。
- Task 4：≥2 独立 judge within-judge delta，dim7/dim8 升、dim4/dim3/dim9 hold（dim9 微降 Δ−1~−2 可接受） → keep。
- `python3 -c "import csv;rows=list(csv.reader(open('plugins/iasi/skills/cleanup/results.tsv'),delimiter='\t'));assert all(len(r)==9 for r in rows);print(len(rows[-1]),'fields last row')"` → 末行 9 列。
- `git log --oneline main -3` → 含 cleanup-wgs --no-ff merge。

## 审阅 Checkpoint

- 计划正文结束（v1）。**⚠️ 本轮头号约束（handoff 硬约束#2）：此处不自起评审 subagent。** 请你手动启用外部 agent 评审这份实施计划；评审通过后告诉我，我再继续落地（Task 1 → 2 → 3 → 4 →（5 条件）→ 6）。外部评审意见我会据以修订计划（修订由外部 reviewer 驱动，非自循环），修订记录届时在此追加。
- **darwin baseline 说明**：baseline 即 Task 4 Step 1 的 A 版（HEAD，264 行 post-R4 状态），Task 4 Step 2 的 same-judge A/B 评分**已自然含基线**（不需要单独跑）。注意 results.tsv 上一条 78.5 是 **07-19 那批 judge** 的分，与本轮 **新 judge** 不可跨 judge 比较（校准 gap）——不要拿 78.5 当本轮基线做错误归因，只信 within-judge delta。
- **框架冲突 + 框架 fix 预判**：
  - **dim7（F3 collapse redundancy）**：预期升（闭合 R3 `dee6e8e` open gap），但须保横切 clause（「规范审计是横切 ≠ 第四 peer」）——这是 R3 counting fix 的关键，丢了 dim7 回归。Task 1 Step 4 + Task 3 Step 2 grep 验。
  - **dim8（F7 null-handler）**：预期升（闭合 R4 `5c03690` open gap：history-depth + no-answer fallback）。
  - **dim4（F5/F6 marker 迁移）**：hold，须保 🛑/🔴 密度（R2 `ceea669` markers 原在资格门/F0/F1，迁到 PHASE 0 稳定门 + 强制 checkpoint）。Task 3 Step 2 grep 验。
  - **dim3/dim9（F8 negation 保留）**：hold，dup-negation（反触发/F2）删可能使 dim9 密度微降（Δ −1 ~ −2 可接受），靠不要路由 + 硬约束 L59 + PHASE 0 🛑 桥接；若 ≥2 judge 一致 ≤ −2 触发 Task 5。
- **开放项（供外部评审一并拍板，非阻塞）**：
  1. 「框架冲突桥接」（signal→action 索引 + co-located 守卫 + 分工注）是否升格为 GLOSSARY.md 术语——**P2-2 修正理由**：它处理的是 darwin dim3/9 与 WGS 两个外部框架的冲突，**超出 GLOSSARY.md「检索难度轴」范畴**（检索难度轴只管「一条规则 co-locate vs defer」的取舍，不管「两个评审框架打架怎么桥接」）。已在 brainstorming `5f54f04` / writing-plans round-2 / handoff round-2 N3 / 本轮 F8 共 4 处验证有效，但**是否升格为稳定术语还是临时手法留给你拍板**——倾向：暂不升格（避免过早抽象），但理由是「范畴不同 + 尚需更多沉淀」，**非** v1 说的「检索难度轴的应用」（那一句站不住，已改正）。
  2. 是否为本轮框架冲突立场建 ADR——三全门槛 borderline（real-tradeoff✓ surprising✓ hard-to-reverse✗），倾向不建（**P3-3 补完整理由**：本轮唯一可能 hard-to-reverse 的是两段段头消失[分层与横切 / 反膨胀原则]，但靠核心边界横切 clause + git history 可恢复，ADR 不必作唯一恢复路径；且 handoff 硬约束#11 + GLOSSARY.md 检索难度轴已记载同款立场）。
- 若批准，按 Task 1 → 2 → 3 → 4 →（5 条件）→ 6 顺序执行；darwin 结论会在 Task 4 回报。

## 修订记录

- **v3（2026-07-26）**：第二轮评审**批准开工**，吸收 4 项非阻塞 polish（主 agent grep 复核）。**P1-2 论证修正（评审抓到我的论证歪了）**：v2 我说「handoff round-2 用区间 150–156 仍 drift，故区间更诚实」——实测 handoff 当前 **140 行**，落 150–156 区间外 = **out-of-band（区间根本没接住），非 drift**。正确结论不是「区间更稳」而是「行数预测本身不准」。体量目标加 out-of-band 警示，Task 3 加 Step 5「wc 落 175–185 区间外停下分析、不默默接受」。**P3-2**：Step 7 `grep -cE '反膨胀原则'`→`grep -cE '反膨胀'`（查所有"反膨胀"不只短语，实测 SKILL.md 当前仅 L251 一处）；**期望 0 的 -cE 全部保留**——期望 0 时 -cE≡-oE\|wc -l，P0-1 口径 bug 只咬非零 marker 计数，不矫枉过正。**P3-3**：开放项 2「倾向不建 ADR」补完整理由（本轮唯一可能 hard-to-reverse 的是两段段头消失，靠核心边界横切 clause + git history 可恢复，ADR 不必作唯一恢复路径）。**P2-3 评审撤回合并建议**：评审核验 L29/L33/L34 确为三条不同 bullet 后撤回，补落地要求——Task 2 三条 prompt 的 expected 措辞须明确指向 L29（handoff-shape）/ L33（代码质量审≠规则审）/ L34（解释≠审计）的具体 disambiguator，避免 judge 评 dim3 时看 expected 都只写"不路由"糊在一起。**memory 泛化**：把 `measure-cjk-length-python-len-not-bytes` 泛化为「count 工具口径 ≠ 语义口径，计数/长度断言一律实测」（涵盖 marker emoji / CJK 字符 / 空行 / 嵌套层级）。
- **v2（2026-07-26）**：吸收外部评审 Agent 报告（**主 agent 全部 grep 复核，非轻信**——P0/P2 断言逐条实测确认）。**P0-1（marker 计数口径 bug）**：实测 `grep -cE '🛑|🔴'`=4（行数）≠ `grep -oE|wc -l`=5（个数），差 1 在 L228 同行 `🔴 CHECKPOINT · 🛑 STOP`。全计划 marker 验证改 `grep -oE '🛑|🔴' | wc -l`；同时 Step 3(c) checkpoint 改**单 marker/行**（去掉原 F0 同行双 marker——R2 flagged 的 mild stacking，合并是清理它的机会），baseline **5 marker/4 gate → 改后 4 marker/4 gate**（gate 数不降）。**P0-2（横切 clause 存活弱断言）**：实测 `横切` 当前命中 L63 段头 + L83 子节；Task 3 Step 2 加双重断言（`grep -cE '分层与横切'`=0 段头清零 + `sed -n '/^## 核心边界/,/^## /p'|grep 横切` clause 落点段内），防残留段头假阳性。**P1-1（judge blind 折扣）**：A/B 行数差 70+、结构差异大，judge 可推断「B=精简版=改后」——blind 是**结构盲非身份盲**；Task 4 Step 3 加声明，within-judge delta 仍可信（同 bias 抵消）、结论不过度宣称 blind 干净。**P1-2（体量算术统一）**：实算 −24−29−5−20−9−1+3+2=**−83**，体量目标统一「约 181 行（区间 175–185）」，澄清各 Step 预期是分量、合计是总量（评审误把 Step 4 的 −24 当总量，实为 F3 分量）。**P2-1（锚点 off-by-one）**：实测 `## 立即执行`=**L261**（L263 是段内首行文本），Step 3(c) 已改正；执行纪律加「每 Step 执行前 `grep -nE '^## '` 重抓行号，计划内行号仅 v1 草拟态」。**P2-2（开放项 1 理由站不住）**：v1 说桥接配方「可能是检索难度轴的应用」——错，检索难度轴只管一条规则 co-locate vs defer，不管两框架冲突；桥接配方**超出其范畴**。理由重构为「范畴不同 + 4 处验证但尚需沉淀，倾向暂不升格，留用户拍板」。**P2-4（Task 6 Step 0 用词）**：「落计划」→「首次提交已存在计划文件」（本文件已在工作区未提交，非新建）。**P2-3 部分驳回**：评审建议合并 governance-soft-vs-hard + rule-explanation-vs-audit 或让 #3 聚焦稳定门——驳回：现有 #3 测不要路由 **L29**（handoff-shape），新两条测 **L33**（代码质量审≠规则审）/ **L34**（解释≠审计），三条测**不同 bullet** 是 failure-mode 编码广度非冗余（dim3/dim9 奖励多失败模式），边界清晰，**保留 5 条新 prompt**，仅澄清矩阵 bullet 标注。
- **v1（2026-07-26）**：基于本会话 `/grill-with-docs` 共识（脊柱 + F3/F4/F6/F7/F8/F9）起草，参照 handoff round-2 / writing-plans round-2 配方。PHASE 5 inline 自检已修 2 处（孤儿扫描 Run A/B 拆分 + dim4 marker 密度），v2 进一步修 P0-1 口径。

## 执行后归因（v3 执行实测 vs 计划，第三轮评审 P0 补）

**背景**：v3 Task 3 Step 5 兜底要求「wc 落 175–185 区间外（<170 或 >190）停下分析、不要默默接受」。执行实测 **159 行**（< 170，out-of-band），主 agent 在对话里做了分析但**未写进持久产物**（commit body / results.tsv note 只记数字）——违反了自己 v3 写进计划的"不要默默接受"。第三轮评审定 P0：流程契约被破，须补归因恢复可追溯。此段即补的持久归因。

**实测分量归因**（git show b48a679 vs 当前，逐 section 量行数；总 264→159 净 −105 vs 计划 −83，超削 **−22**）：

| 分量 | 实测 Δ | 计划 | 超削 | 性质 |
|---|---|---|---|---|
| 强制 cleanup checkpoint 压缩 | −26 | −20 | **−6** | **有益**：F0(3 risk bullets)+F1(段) ~10 行 → checkpoint ~3 行，正是 R2 flagged 的同行双 marker stacking 清理 |
| 软提醒 压缩 | 何时使用 +2（1 行段落） | ~+7 fold | **−5** | **有益**：mid-model 校准（压成高密度 1 行，非 7 行散文） |
| 资格门 bullet 化 | −9（14 行→5 嵌套 bullet） | −5 | **−4** | **有益但须正名**（P1-1）：判据**压缩成可核对嵌套 bullet**，非"原话展开"——这是 dim8 +1 的部分来源（判据清晰化），非单纯 F7 fallback |
| 分层行数估计偏 | −26 | −24 | −2 | 估计偏（实测 26 行） |
| null-handler F7 | ~+1 | +3 | −2 | history-depth 已在原 PHASE 0，实际仅 +1 行 no-answer fallback |
| 反膨胀 + 取整 | −10 | −9 | −1 | — |

**接受（非疏漏）**：所有 load-bearing 内容存活，Task 3 Step 1-4 实证——资格门 4 条件→稳定门 bullets、F0/F1→checkpoint、F2→硬约束 L54-55、反膨胀 checklist→PHASE 2 优先删除表、分层横切 clause→核心边界、4 marker→存活。超削 −22 **全部来自有益压缩**（mid-model 校准 + dim4 stacking 清理 + 判据 bullet 化），**非丢内容**。159 行结构完整、darwin KEEP、PHASE 1-4 步骤核零改动。接受这个 out-of-band 结果。

**dim8 dry-run 局限（P2-1）**：blind A/B judge 无法实跑 prompt，dim8 只能 dry-run 推演——J2 捕到 F7 no-answer fallback（+1）、J1 dry-run 中性（0）。**dim8 +1 是单 judge、最低显著量（P2-2）**：不显著为负即 KEEP 成立，但**非"强证据闭合 R4 gap"**；真严验需 darwin full_test 实跑（darwin 演进方向，非本轮 scope）。

**分工注密度观察（P1-2，非硬阈值）**：Step 6 inline「非冗余」分工注实测 2 处（不要路由 L29 + 硬约束 governance L60），handoff N3 同款 1 处；两轮均 dim7 净正。J1 警告"略显絮叨"。**观察**：N3 分工注模式密度若续增（>2 处/skill）须警惕侵蚀 dim7——但无硬阈值证据，记为趋势观察非规则。

**方法论教训（已入 memory）**：计划里写的"若 X 则停下分析"兜底，执行时到了 X 必须真停下、分析、**并记进持久产物**（commit/results/plan），不能只在对话里分析。写进计划 ≠ 执行它——本轮复现了 handoff out-of-band 且未持久归因，正是 v3 Task 3 Step 5 想防的失败模式。
