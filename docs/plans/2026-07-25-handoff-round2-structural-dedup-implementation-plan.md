# handoff skill 第二轮结构去重 + 中模型校准 实施计划

> v3（2026-07-26）：吸收评审 Agent 第二轮报告（主 agent 全部 grep 复核，非轻信）。P1 吸收 3 项计数订正——A（Step 2 入口 L55→L56，L55 实为空行）/ B（不要路由段 7→6 条，实测 6）/ C（三清单各 6 条非 5，「5 项」是主动并 #1+#2 的决策、非「对齐既往」）。C3（Step 2 子顺序 c↔d 互换：先立只读锚再删 negation，否则自造中间态孤儿——最关键）。C1（L136 改半指针半守卫，更合检索难度轴）。C2（darwin 2 judge 方向相反时 spawn 第 3 judge）。P2 吸收 A（dim9「5/6」改无歧义「不要做段 6→1+翻 2 正面」）/ B（跨会话 memory 工具 inline 定义，GLOSSARY.md 未定义）/ D（PHASE 1 62→63 行）。**回怼 P2-C**：硬约束 bullets 实测 L37-41（L36 空行），计划原引正确，评审该条自相矛盾（同规律抓出 PHASE1 L55/L56 却对硬约束漏算空行）。体量目标放宽 149-155→150-156。
>
> v2（2026-07-25）：吸收评审 Agent 报告（P0 全部已核查无误：锚点 grep 实测全对、零行为丢失核查通过、darwin 协议合规）。P1 吸收 6 项——L136 体量估错(−2→−0)、6源/5项表述对齐、Step 2 子顺序显式化、L113 memory-工具 nuance 入正面锚、judge prompt 绝对路径、dim9 目标改「预期微降」+ Task 5 回退首选 L113。P2 吸收 4 项（id 顺序/L116 清理/PHASE3 done 重叠/commit msg 对齐）。
>
> v1（2026-07-25）：基于本会话 `/grill-with-docs` 共识（F1–F7 决策）起草，参照 writing-plans round-2（`98ba477`/`3455cd7`）走通的 MERGE-before-DELETE + darwin blind A/B 配方。

## 目标

- 对本地 `handoff` skill 做 writing-great-skills 第二轮优化：**结构去重（F1/F2/F3/F5）+ 中模型校准（F4/F6）+ test-prompts 补全（F7）**。
- **契约：零行为丢失**。每条被删/被移的规则必须在存活副本里找得到；PHASE 0–3 的**步骤结构与既有 handler 不动**，只收敛重复表述、强化完成判据与 leading-word 锚。
- 体量目标：167 行 → 约 150–156 行（v3 放宽上限——P2-D/C3，避免为凑数过度压缩）。明细：PHASE 1（实测 **63 行** L54-116，v2 误作 62——P2-D）三清单合一（各 6 条→5 项）+ negation 缩减 + L116 清理 ≈ −15 行（63→约 48）；materiality L136 单行 bullet 缩半指针半守卫 ≈ **0 行**（v3-N1：python3 `len()` 实测 **114 字符**/282 字节，与 L137（93）同量级，**非长句**；v2/v3 误称「283 字符长句」是把 UTF-8 字节数当字符数——单行→单行不减行）；顶部轻量合并 ≈ −2 行；PHASE done 判据 + 锚词 ≈ +3 行；净减约 14 行。
- darwin 目标：dim7（结构/去重）不降反升；dim4（视觉检查点，R3 已修）hold；dim3（失败模式编码）靠 co-located 守卫（不要路由段 + PHASE 0 🛑 + L112）hold；**dim9（反例黑名单）预期微降（Δ −1 ~ −2 可接受）——框架冲突区：不要做段反例 6→1（留 L112 hard guardrail）+ 翻 L113-114 为正面（v3-P2-A：弃用歧义的「5/6」表述，改无歧义的段级事实），dim9 历史强度正来自「不要做」6 条黑名单，缩到 1 条密度下降属已知代价，靠不要路由段（实测 **6 条**，v2 误作 7——P1-B）+ L112 桥接，若 ≥2 judge 一致显著降（≤ −2）触发 Task 5 回退 L113**；dim1/dim8（清晰度/可执行性）靠 done 判据 + 锚词预期微升。

## 架构快照

- 主干 PHASE 0–3 的步骤结构与 handler 不动。改动集中在重复表述层 + 完成判据层 + 锚词层。
- **PHASE 1 三清单合一（MERGE then DELETE）**：当前把同一组 6 个证据源列了 3 遍——`证据优先级`（L58-64，ranked）/ `必须做的证据收集`（L66-72，imperative）/ `建议执行顺序`（L81-87，ordered）。三者是同一组 {同会话历史/compact/可见对话/todo/git/文件} 的三种排列，优先级即顺序。合并为 1 份 ranked+imperative 清单（既是优先级又是收集动作），删执行顺序段，把 net-new nuance（L72 项目级指令门槛、L74-79 命令清单、L89-90 缺工具降级）就近并入。
- **materiality 拆分（检索难度轴）**：散落 7 处。按检索难度拆——L136「不扭曲原话/不拼一句/不改写」是**泛化结构规则**（中模型能从 L39 主定义检索）→ MERGE 回 `硬约束` L39；L145「二次复核相关性」+ L153「三次按目标筛」是**微妙情境守卫**（silent-drift 型，跨长文档检索不可靠）→ co-locate 保留在各自 PHASE 触发点 + materiality leading-word 锚；模板 L5/L20/L66 保留（输出时离 SKILL 远，是 single source for output-time）。
- **negation 缩减（WGS negation cure）**：`不要做这些事`（L108-114）6 条。L109-111（编辑/创建/改 git）是 `硬约束` L37「保持只读」的否定重述 → DELETE（靠 PHASE 1 入口 只读 锚 + L37）；L112（不跑 install/build/test）保留作 hard guardrail（中模型 silent-drift 型：爱「跑个测试更彻底」），配正面「只做只读收集」；L113-114（不补造/不包装弱推断）翻正面——**注意 L113「用 memory 补造缺失事实」指跨会话 memory 工具（CLAUDE.md/auto-memory），与 L38「直接证据优先于回忆」（回忆=模型内部 recall）不同义**（P1-R4），PHASE 1 入口正面锚须显式覆盖「只用本会话/chat 内直接证据，不从跨会话 memory 工具补造」；L114「弱推断包装强结论」已被 L133 verified/inferred/unknown 区分覆盖。dim9 预期微降（见目标段），Task 5 桥接首选回退 L113（silent-drift 反例，darwin 奖励显式编码）。
- **完成判据 + leading-word（中模型校准）**：PHASE 1/2/3 各加 1 行 checkable+exhaustive done 判据（PHASE 0 已有 🛑 早退）；materiality 作核心 leading word（已是 token，跨 SKILL/模板统一），PHASE 1 用 证据优先/只读 锚，输出用 自包含 锚。
- **不动**：description（路由面敏感，runtime-INCLUSIVE 列举属 darwin 例外）、PHASE 0 🛑 gate（R3 已修 dim4）、不要路由段（routing failure mode，dim3/dim9 加分）、interface.yaml、GLOSSARY.md / docs/adr/（本轮决策不达 ADR 三全门槛，检索难度轴已存在并被复用）。
- **框架冲突预判（硬约束#9）**：handoff 的失败模式已**分布在触发点 co-locate**（不要路由段 + PHASE 0 🛑 + L112），非集中表。本轮不新建诊断索引表（与 writing-plans/brainstorming 不同——那两者的红灯段是独立冗余段需转索引表；handoff 的失败面已在触发点，无需再聚）。风险点仅 F3 删 negation 可能使 dim9 微降 → 靠保留 L112 + 不要路由段 + PHASE 0 🛑 桥接，within-judge delta 判定。

## 全局约束

- **零行为丢失**：每个删除点须先确认存活 single source；MERGE 优先于 DELETE——独有 nuance 先并入存活家，再删冗余表述。
- **PHASE 0–3 步骤结构与 handler 不动**；例外仅：PHASE 1 内部三清单合一（同组源的表述收敛，收集动作与证据源不变）、negation 段缩减（守卫语义迁移到正面锚/守卫）。
- **本轮一起补 test-prompts（F7）**：4 → 约 9 条，覆盖 F1-F6 改动面 + 已知缺口（边界路由/缺证据降级/materiality 三阶段/只读守卫）。新 prompt 针对新结构设计，故须 Task 1（SKILL.md 重构）先于 Task 2（test-prompts）。
- **只改 handoff 一个 skill**：不动 brainstorming / writing-plans / cleanup，不动上游冻结的 5 个 skill。
- **中模型校准**：删低密度复述（同组源讲 3 遍那种），保留高密度锚词；定位用章节锚点字符串，行号仅作当前态提示（v1 实测 grep 锁定，执行时以锚点为准）。
- **darwin 硬约束**：跨 judge 总分不可比（07-19 的 80.8/85.5 是彼时 judge 的分，不可跨 judge 当基线），只信 within-judge delta（blind A/B 同评两版）；judge 不被告知重点 dim、不注入 rubric 正文、不输出 keep/revert（keep/revert 由主 agent 跨 judge 整合）；dim8 实测必须 spawn 独立 Agent 子 judge，禁主 agent 自评；results.tsv 用 Python 追加（9 字段、note 单行 `;` 分隔、assert 无 tab）；结果卡交付 HTML（本 WSL 无 PNG 渲染）。
- **分支**：feature 分支 `handoff-round2`，--no-ff merge 回 main。commit footer 沿用仓库惯例 `Co-Authored-By: Claude <noreply@anthropic.com>`。

## 输入工件

- 已批准设计：本会话 `/grill-with-docs` 共识（F1–F7 决策，见上方架构快照）。
- 目标 skill：`plugins/iasi/skills/handoff/SKILL.md`（当前 167 行）+ `test-prompts.json`（当前 4 条）。
- 形态参照：`plugins/iasi/skills/writing-plans/SKILL.md`（220 行，round-2 MERGE-before-DELETE 去重 + 红灯索引表样板）+ `plugins/iasi/skills/brainstorming/SKILL.md`（246 行，桥接样板）。
- 诊断 rubric：`~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md`。
- 术语/决策上下文：`GLOSSARY.md`（检索难度轴、test-mapped failure mode、中模型校准）、`docs/adr/0001-two-track-design-pull-only-plan-handoff.md`。
- handoff：`docs/handoff/2026-07-25-handoff-skill-optimization-handoff.md`（10 个硬约束）。
- 计划样板：`docs/plans/2026-07-25-writing-plans-round2-structural-dedup-implementation-plan.md`（含 darwin judge prompt 模板、MERGE-before-DELETE 模式、框架冲突判据表）。

## 文件结构与职责

- Modify: `plugins/iasi/skills/handoff/SKILL.md` — 结构去重 + done 判据 + 锚词（Task 1）
- Modify: `plugins/iasi/skills/handoff/test-prompts.json` — 补全到约 9 条（Task 2）
- Modify: `plugins/iasi/skills/handoff/.gitignore`（新建或追加）— 忽略 `.darwin/` 临时评分文件（Task 4）
- 验证：零行为丢失自检（Task 3，只读）
- darwin 实测：≥2 独立 judge 盲评 A/B（Task 4，只读 + results.tsv 追加）
- 视情况桥接（Task 5，条件触发）
- 收口：feature 分支 commit + --no-ff merge（Task 6）

## 任务清单

### Task 1: handoff SKILL.md 重构（结构去重 + 中模型校准，按区域）

- 目标：按区域收敛重复表述 + 强化完成判据与锚词。PHASE 0–3 步骤结构与 handler 不动。
- 涉及文件：`plugins/iasi/skills/handoff/SKILL.md`
- 为什么是单任务：F1/F3/F4/F5/F6 在 PHASE 1 区域强耦合——三清单合一会吸收 negation 处理、只读锚、done 判据；拆分会产生编辑同一区域多次的中间态。各区域（PHASE 1 / 硬约束 / PHASE 2-3 / 顶部）作为 Step 分割，diff 可读。编辑按**章节锚点字符串**定位（非行号）。
- 接口契约
  - Consumes：已批准设计（F1/F2/F3/F4/F5/F6）
  - Produces：重构后的 SKILL.md（PHASE 0–3 步骤结构原样；PHASE 1 三清单合一 + negation 6→1；materiality nuance 合并；各 PHASE done 判据；leading-word 锚）
- 验证范围：行数落到约 150–156；存活副本 grep 验每个删除点的**触发条件 + 动作**有家；PHASE 0–3 步骤结构未变。

- [ ] Step 1: 改动前检查（基线快照）
  - Run: `cd plugins/iasi/skills/handoff && wc -l SKILL.md && grep -nE '^## |^### ' SKILL.md`
  - Expected: 167 行；章节含 `## PHASE 1: 收集程序化上下文`（L54）、`## 硬约束`（L35）、`## PHASE 2: 提炼上下文`（L118）、`## PHASE 3: 格式化输出`（L150）。记录为比对基线。

- [ ] Step 2: PHASE 1 重构——三清单合一 + 锚词 + negation 缩减 + done 判据（F1 + F3 + F4 + F5-L56/L23 + F6-证据优先/只读锚）
  - 锚点：`## PHASE 1: 收集程序化上下文` 到下一个 `## ` 即 `## PHASE 2` 之前（实测 L54-116）。
  - Change（**按子顺序执行，每步后 grep 验存活，避免中间态孤儿——P1-R3**）：
    - **(a) MERGE 独有 nuance 进新清单**：`证据优先级`（L58-64，ranked）+ `必须做的证据收集`（L66-72，imperative）+ `建议执行顺序`（L81-87，ordered）→ 合并为 1 份 ranked+imperative 清单，**5 项**（v3-P1-C 修正：原三清单**各 6 条**——实测 证据优先级 L59-64 / 必须做 L67-72 / 执行顺序 L82-87 均 6 条；本轮**主动并 #1 同会话历史 + #2 compact 历史**为一项，compact 作子注，6→5，语义零丢失。**非**「对齐 L66-72 既往」——L66-72 既往亦 6 条，只是它并了 compact 而另加了「项目级指令门槛」。合并后：`#1 同会话历史（含更早轮次与 compact/pre-compaction 历史，作子注）/ #2 当前可见对话 / #3 当前 todo / #4 只读 git / #5 直接读取必要文件`）。**MERGE 独有 nuance**：L72「只有在项目级指令确实影响当前工作时才读取」并入 #5 项下；L74-79 命令清单（`git diff --stat HEAD~10..HEAD` / `git status --porcelain` / `rg` / `ls` / `pwd`）作为 #4「只读 git」项的命令子列保留（「怎么做」的具象，非重复）；L89-90「缺 same-session/todo 工具则从可见对话开始并记缺失」「git/文件检查只在实质提升交接质量时做」作为清单后条件注保留。
    - **(b) DELETE 冗余清单**：删 `建议执行顺序` 整段（L81-87，纯重排，无独有内容——git 已在命令子列拆成 diff-stat + status）；删 `必须做的证据收集` 中与优先级逐条重复的 imperative 重述（L67-71），独有 L72 已在 (a) 并入。**删 L116**「如果任何证据源不可用，明确记下来，然后继续」——是 `硬约束` L40 的低密度复述（P2-R2），语义并入下方 (e) done 判据。
    - **(c) 只读锚 + 证据优先锚 + L113 nuance + 严格 framing + memory 定义**（F6 + P1-R4 + P2-R6 + v3-P2-B；**先于 (d) 立锚——v3-C3：negation 删除依赖此锚存活，v2 的 (c)negation↔(d)anchor 顺序会自造中间态孤儿**）：PHASE 1 入口句（**原 L56**——v3-P1-A 修正：`## PHASE 1` 标题在 L54、L55 为空行，「仅使用只读动作收集具体证据」实为 L56；v2 误作 L55）扩为**严格只读收集**锚，含三义——「**证据优先**：只用本会话/chat 内直接证据（同会话历史/可见对话/todo/git/文件），缺证据标 `未知`/`无`，**不从跨会话 memory 工具补造缺失事实**（承接 L113 nuance）；**只读**：仅只读动作，不写文件/不改 git/不跑 build-test（承接 L109-111 + L112）；严格模式交接工作流。」吸收原 L23 语义（L23 在 Step 5 删）。**memory 定义（v3-P2-B）**：本轮显式界定——L113「用 memory 补造」+ L104「而不是 memory」的「memory」指**跨会话 memory 工具**（CLAUDE.md / auto-memory 类外部持久化），区别于 L38「优先于回忆」+ L103「对话回忆」的「回忆」= 模型内部 recall；GLOSSARY.md 未定义此术语，故 inline 定义、不作为既定术语引用。
    - **(d) negation 缩减**（L108-114，**锚已由 (c) 立好方可删**）：DELETE L109-111（编辑/创建/改 git——靠 (c) PHASE 1 只读锚 + `硬约束` L37）；保留 L112「不跑 install/build/format/test」作 hard guardrail，配正面「只做只读收集」**（与 (c) 入口锚分工——v3-N3：入口锚是只读总纲，L112 是解码型 silent-drift 守卫——中模型收集末尾常生『跑个测试更彻底』冲动，L112 显式命名此具体失败路径；一总一分、非同义重复，防 darwin dim7 把 build-test 误判冗余）**；L113-114 翻正面——L113 锚到 (c) 入口正面锚（「不从跨会话 memory 工具补造」），L114「区分 verified facts / inferred context / unknowns，弱推断不包装成强结论」（正解已在 L133，此处显式锚到收集点）。
    - **(e) done 判据**（F4 + P2-R2）：PHASE 1 末（`## PHASE 2` 之前）加一行 checkable+exhaustive 判据：`证据收集完成判据：上方 5 源已按可用性逐一检查（不可用的已记 `未知`/`无`——含被删 L116 语义）；下方提炼问题都能基于证据回答；全程未做写操作。`
    - **保留不动**：`收集完证据后需要回答的问题`（L92-99，7 问，是提炼的 single source，PHASE 2 L143 已指回）、`证据冲突处理规则`（L101-106，5 条，distinct reference）。
  - 理由：三清单是同一组源（5 项）的三种排列，合并为 ranked+imperative 单清单是 single-source-of-truth；negation 按 WGS cure 翻正面、留 hard guardrail（L112）；L113 的跨会话 memory 补造是 silent-drift 守卫，正面锚显式覆盖（检索难度轴：微妙情境守卫 co-locate）；done 判据抗中模型 premature-completion；锚词压缩非膨胀。
  - 预期：PHASE 1 约 63→约 48 行（v3-P2-D：实测 63 非 62）；negation 6→1（L112）+ 2 条正面化 + L116 删（并入 done 判据）。

- [ ] Step 3: 硬约束 materiality 主定义合并 + materiality 核心锚（F2-L136→L39 + F6-materiality 核心）
  - 锚点 A：`## 硬约束` 段 L39（materiality 主定义：「对 用户请求/显式约束 先按 materiality 过滤，再 verbatim 复制...过滤后为空写 无」）。
  - 锚点 B：`## PHASE 2` 段 `提炼硬规则` L136（「用户请求与显式约束沿用『硬约束』中的 materiality 过滤 + verbatim 复制规则...此外不要把多个原话拼成一句概括，也不要改写保留下来的原话；已过期...要省略」）。
  - Change:
    - **MERGE-B（半指针半守卫——v3-C1，修正 v2 的完全 defer）**：把 L136 的「已过期对继续工作不重要的引用省略」并入 `硬约束` L39 materiality 主定义（泛化结构规则，中模型能从 L39 检索）。但「**不拼成一句概括 / 不改写保留下来的原话**」**保留在 L136 作 inline 守卫**（半指针半守卫，非完全 defer）——理由（检索难度轴）：L136 处于 PHASE 2 提炼触发点，正是中模型把多条原话压缩成一句的 silent-drift 高发位；把这两条完全 defer 回 L39（远）赌中模型压缩时会主动检索，跨 compact 长会话里未必稳。故 L136 改为：「用户请求与显式约束按 `硬约束` 的 materiality 规则处理（过滤后 verbatim 复制；**不拼成一句概括、不改写原话**——此处 inline 提醒；过期省略见 `硬约束`）」。主定义全密度在 L39，压缩守卫 co-locate 在 L136 触发点。
    - **materiality 核心锚**（F6）：确认 `materiality` 作为 leading word 在 SKILL（L39/L136/L145/L153）+ 模板（L5/L20/L66）统一作 token 使用（已是，本轮保持一致性，不新造同义词）。
  - 理由：L136「过期省略」是泛化结构规则 → 并回 L39；但「不拼一句/不改写」是 PHASE 2 压缩点的 silent-drift 守卫（检索难度轴：微妙情境守卫须 co-locate）→ 保留 L136 inline（v3-C1，修正 v2 的完全 defer）；L145/L153 阶段守卫不动（Step 4 处理）。
  - 预期：约 **0 行**（v3-N2 修正 v2 残留：L136 单行 bullet（114 字符）→ C1 半指针半守卫仍是单行；若把『过期省略』并入 L39 使该 bullet 软换行，`wc -l` 不变——实现时留意 L39 勿压扁难读）。

- [ ] Step 4: PHASE 2/3 materiality 守卫 co-locate + done 判据 + 自包含锚（F2-L145/L153 + F4-PHASE2/3 + F6-自包含锚）
  - 锚点 A：`## PHASE 2` 段 `提炼时重点考虑这些问题` L145（「重新审视已引用的用户请求或约束：对继续工作是否仍然真正重要；不再重要的应弱化或省略（区别于『硬约束』里的初次 materiality 过滤，这是二次复核）」）。
  - 锚点 B：`## PHASE 3` 段 L153（「先根据下一个 chat 的目标再次做 materiality 筛选，再填充模板」）。
  - Change:
    - **守卫保留 + materiality 锚**（F2）：L145（二次复核）+ L153（三次按目标筛）**保留原位**（微妙情境守卫，co-locate 到各 PHASE 触发点），各补一句明确这是 materiality 的第 N 次筛选、指向 `硬约束` 主定义。L145 已有「二次复核」措辞，强化为「materiality 二次复核：已引用请求/约束是否仍对续接重要（初次过滤见 `硬约束`）」；L153 强化「materiality 三次筛选：按下一个 chat 目标再筛一次」。
    - **done 判据**（F4）：PHASE 2 末加 `提炼完成判据：verified facts / inferred context / unknowns 已区分；用户原话 verbatim 保留（未拼概括、未改写）；无关内容已省略。`；PHASE 3 末加 `格式化完成判据（自检 yes/no，不重述 L154/模板规则——P2-R3）：空段已写 无；未新增模板外章节；单外层代码块 + 说明区在外（复检 L154 已立）。`
    - **自包含锚**（F6）：`重要约束` 段 L160「要提供一份不依赖当前 chat 也能使用的自包含摘要」保留为 **自包含** 锚（输出 virtue，已是 token）。
  - 理由：L145/L153 是 silent-drift 型守卫（跨长文档检索不可靠），检索难度轴判定须 co-locate，不 defer；done 判据抗 premature-completion；自包含锚锚住输出层。
  - 预期：约 +3 行（守卫强化措辞 + 2 条 done 判据）。

- [ ] Step 5: 顶部轻量清理（F5-L20+L21-22 / L23）
  - 锚点：`## 何时使用` 段 L20-23。
  - Change:
    - L20「默认按显式交接意图触发。」+ L21-22「仅因为当前 chat 很长、质量下降或上下文窗口接近上限，不足以单独路由到这里。」→ 合并为一句：「默认按显式交接意图触发——仅因 chat 很长、质量下降或窗口接近上限，不足以单独路由到这里。」
    - L23「这是一个严格模式的交接工作流：证据优先，不要猜。」→ 语义已由 `硬约束` L38「直接证据优先于回忆」+ L40 缺证据写未知 承载，且「证据优先」锚已移入 PHASE 1 入口（Step 2）。**DELETE L23**（靠 L38 + PHASE 1 锚存活）。
  - 理由：L20-22 合并消除单行后接展开的冗余；L23 是 L38 的散文复述（低密度），锚词化后无须再散文重述。
  - 预期：约 −2 行。

- [ ] Step 6: 改动后验证
  - Run: `wc -l SKILL.md`（期望约 150–156）&& `grep -nE '^## ' SKILL.md`（期望章节齐全，无新增/丢失）&& `grep -cE '建议执行顺序' SKILL.md`（期望 **0**）&& `grep -cE '必须做的证据收集' SKILL.md`（期望 **0**，已并入）&& `grep -cE '如果任何证据源不可用，明确记下来' SKILL.md`（期望 **0**，L116 已删并入 done 判据）&& 存活副本 + 孤儿扫描（见 Task 3）。
  - Expected: 行数达标；执行顺序段/必须做段/L116 消失；PHASE 0/1/2/3 步骤结构与 handler 零改动（diff 增删仅落在 Step 2-5 位点）。

### Task 2: test-prompts 补全（4 → 约 9 条，F7）

- 目标：补 test-prompts 覆盖 F1-F6 改动面 + 已知缺口，使 darwin 评估与回归有足够触点。
- 涉及文件：`plugins/iasi/skills/handoff/test-prompts.json`
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md（新 prompt 针对新结构设计）
  - Produces：约 9 条 test-prompts（含 expected）+ 覆盖矩阵
- 验证范围：JSON 合法；每条 prompt 映射到一个 PHASE/守卫；覆盖矩阵无盲区。

- [ ] Step 1: 新增约 5 条 prompt（保留现有 4 条——P2-R1：实测 id 顺序为 `[1, 2, 4, 3]` 非 `[1,2,3,4]`，追加时新 id 从 5 起，可选重排为 1-9 连续）
  - Change: 追加：
    - `boundary-should-not-route-code-review`：代码评审/缺陷分析请求 → 不产出 handoff 代码块，属『不要路由』。（routing failure mode）
    - `boundary-should-not-route-changelog`：PR/commit/release 摘要或 changelog 请求 → 不路由。（routing failure mode）
    - `missing-evidence-degradation`：模拟环境无 same-session history / todo 工具 → 显式记缺失证据源，从当前可见对话开始，不补造。（测 F1 并入的 L89-90 缺工具降级 + 只读锚）
    - `materiality-three-stage`：模拟跨 compact 的长会话，显式目标「补单测」→ 测 materiality 三阶段（初次过滤 / 二次复核相关性 / 三次按目标筛）守卫是否 co-locate 生效，省略与目标无关的历史讨论。（测 F2 守卫 + L145/L153）
    - `read-only-collect-guard`：诱导在收集阶段跑 `npm test` 或编辑文件确认状态 → 触发只读锚 + L112 hard guardrail，拒绝写操作/build/test，只做只读收集。（测 F3 L112 + 只读锚）
  - 现有 id 3（explicit-goal-drives-materiality）与新增 `materiality-three-stage` 有重叠但侧重不同（前者单次 materiality，后者跨 compact 三阶段）——保留两者，覆盖单次 vs 多阶段。
  - Expected: JSON 合法，约 9 条，每条有 prompt + expected。

- [ ] Step 2: 覆盖矩阵（映射 prompt → PHASE/守卫）
  - 验证：下列映射无盲区——
    | prompt | 覆盖 |
    |---|---|
    | happy-path-typical-handoff | 全模板 + 第一人称 + 单代码块 |
    | boundary-recap / code-review / changelog | 不要路由段（routing failure mode） |
    | boundary-low-content-early-exit | PHASE 0 🛑 早退 |
    | explicit-goal-drives-materiality | materiality 初次过滤 |
    | materiality-three-stage | materiality 二次复核 + 三次筛选（F2 守卫） |
    | missing-evidence-degradation | PHASE 1 缺工具降级 + 只读锚（F1） |
    | read-only-collect-guard | 只读锚 + L112 hard guardrail（F3） |
  - Expected: F1-F6 改动面均有 prompt 覆盖；dim3/dim9（failure mode 编码）有 ≥4 条 routing/guard prompt 支撑。

### Task 3: 零行为丢失自检（只读）

- 目标：实证「零行为丢失」，**同时验触发条件 + 动作**有存活 single source。
- 涉及文件：只读 Task 1 产物
- 接口契约
  - Consumes：Task 1 重构后的 SKILL.md
  - Produces：自检结论（pass / 需补归属）
- 验证范围：下列 4 项全部通过。

- [ ] Step 1: 被删规则存活副本检查（触发条件 + 动作，位置敏感）
  - Run:
    - 三清单合一后的 5 项：`grep -nE '同会话历史|compact|当前可见对话|todo|git diff --stat|git status|直接读取' SKILL.md` → 期望 5 项**各出现一次**（在合并后的 ranked+imperative 清单 + 命令子列），不出现 3 份独立清单（compact 作 #1 同会话历史子注）。
    - L72 项目级指令门槛：`grep -nE '项目级指令' SKILL.md` → 期望命中且落在 PHASE 1 合并清单的「直接读取必要文件」项下。
    - negation 删后存活：`grep -nE '编辑文件|创建文件|改变 git 状态' SKILL.md` → 期望仅命中 `硬约束` L37「保持只读」的正向表述（或 PHASE 1 只读锚），negation 段原 L109-111 措辞 0 命中。
    - L112 hard guardrail：`grep -nE 'install|build|format|test' SKILL.md` → 期望 L112 保留（hard guardrail + 正面「只做只读收集」配对）。
    - **L113 memory-工具 nuance 存活（P1-R4）**：`grep -nE '跨会话|memory 工具|memory 补造|本会话.*直接证据' SKILL.md` → 期望 PHASE 1 入口正面锚显式含「只用本会话/chat 内直接证据，不从跨会话 memory 工具补造」语义（不止 L38 的「回忆」措辞）。
    - L114 正面化：`grep -nE 'verified|inferred|unknowns' SKILL.md` → 期望正面措辞落在 PHASE 1 收集点（不只 L133）。
    - L23 删后存活：`grep -nE '证据优先|不要猜' SKILL.md` → 期望「证据优先」锚落在 PHASE 1 入口，「不要猜」可删（靠 L38 + 缺证据写未知）；L23 原散文句 0 命中。
    - **L116 删后存活（P2-R2）**：`grep -nE '如果任何证据源不可用，明确记下来' SKILL.md` → 期望 **0 命中**（语义并入 PHASE 1 done 判据 + `硬约束` L40）。
  - Expected: 每个删除点的触发条件 + 动作有存活 single source；无孤儿。

- [ ] Step 2: materiality 拆分存活检查（主定义 + 守卫）
  - Run:
    - 主定义全密度：`grep -nE 'materiality' SKILL.md` → 期望 L39 主定义含「过滤 + verbatim + 不拼概括 + 不改写 + 过期省略」（Step 3 MERGE-B 并入），L136 缩为指针句。
    - 二次/三次守卫：`grep -nE '二次复核|三次.*筛选|三次.*materiality' SKILL.md` → 期望 L145（二次复核）+ L153（三次按目标筛）co-locate 保留在 PHASE 2/3 触发点。
  - Expected: materiality 泛化规则 single source 在 L39；阶段守卫 co-locate 不动。

- [ ] Step 3: 孤儿指针扫描（加宽）
  - Run: `grep -nE '建议执行顺序|必须做的证据收集|上方.*证据优先级|参见.*执行顺序' SKILL.md`
  - Expected: **0 命中**（被删清单段无残留外指引用）。

- [ ] Step 4: PHASE 0–3 步骤结构未变检查
  - Run: `git diff -- plugins/iasi/skills/handoff/SKILL.md`，逐 hunk 核对——增删行须全部落在 Step 2（PHASE 1 重构）/ Step 3（硬约束+L136）/ Step 4（PHASE 2-3 守卫+done）/ Step 5（顶部清理）四个位点。PHASE 0 🛑 gate、不要路由段、证据冲突规则、7 问清单零改动。
  - Expected: 主干步骤结构与 handler 无改动；diff 可追溯到 Step 2-5。

### Task 4: darwin full_test 实测（blind A/B）

- 目标：用独立 judge 盲评改后(B) vs 改前(A)，within-judge delta 验证 dim7 不降、dim4 hold、dim3/dim9 hold、dim1/dim8 预期微升。
- 涉及文件：只读 SKILL.md（A/B 两版落 `.darwin/`）；追加 `results.tsv`
- 接口契约
  - Consumes：Task 1–3 通过 + Task 2 新 test-prompts
  - Produces：≥2 judge 的 per-dim 双分数 + Δ；results.tsv 新行
- 验证范围：≥2 独立 Agent 子 judge；每个 judge 同评 A/B 两版；judge 不被告知重点 dim、不注入 rubric、不输出 keep/revert。

- [ ] Step 1: 落 A/B 两版到 repo-local 临时文件
  - Run:
    - `mkdir -p plugins/iasi/skills/handoff/.darwin`
    - A 版：`git show HEAD:plugins/iasi/skills/handoff/SKILL.md > plugins/iasi/skills/handoff/.darwin/ho_A.md`（round-2 改前 167 行版）
    - B 版：`cp plugins/iasi/skills/handoff/SKILL.md plugins/iasi/skills/handoff/.darwin/ho_B.md`（Task 1 产物）
    - 确保 `.darwin/` 在 `.gitignore`（新建或追加一行 `.darwin/`）；不用裸 `/tmp`（WSL sandbox TMPDIR 风险）。
  - Expected: 两版文件就绪；`.darwin/` 不入 git。

- [ ] Step 2: spawn ≥2 独立 judge（Agent 工具，独立 context，blind）
  - Run: 每个 judge 的 prompt **只给两个文件路径** `ho_A.md` / `ho_B.md`，**不告诉哪个是改前/改后、不点名重点 dim、不注入 darwin rubric 正文**（让 judge 自己读 `~/.claude/skills/darwin-skill/SKILL.md` 的 9-dim rubric）。要求每个 judge 按 9-dim 全评两版，输出**每维 A_score、B_score、Δ(B−A)**，**不要给 keep/revert 结论**。
  - prompt 模板（spawn 时照填，只换 judge 编号；**用绝对路径**——P1-R5：子 judge cwd 不保证在 repo root）：
    ```
    读取以下两份 SKILL.md（标记 A 和 B，身份未知，不要假设哪个是改前/改后）：
      A: /home/iasi/workspace/m/plugins/iasi/skills/handoff/.darwin/ho_A.md
      B: /home/iasi/workspace/m/plugins/iasi/skills/handoff/.darwin/ho_B.md
    按 /home/iasi/.claude/skills/darwin-skill/SKILL.md 描述的 9-dim rubric（dim1-dim9）各评两版，
    输出 markdown 表格：| dim | A_score | B_score | Δ(B−A) | 简评 |
    不要给 keep/revert 结论；不要预设重点 dim。
    ```
  - 硬约束：禁主 agent 自评（darwin 反例 #1）；judge 盲评不知 A/B 身份；keep/revert 不在 judge 做。
  - Expected: ≥2 份独立 per-dim 双分数 + Δ。

- [ ] Step 3: 主 agent 跨 judge 整合 keep/revert
  - Run: 主 agent 汇总 ≥2 judge 的 per-dim Δ，看方向一致性。重点 dim（dim7/dim4/dim3/dim9——由主 agent 事后识别，judge 不知情）判据：dim7/dim4/dim3 Δ 不显著为负（> −1）即 keep；**dim9 预期微降（Δ −1 ~ −2 可接受，框架冲突区，见目标段）——Δ 在 −2 以内且 ≥2 judge 方向一致判属「框架冲突可接受」即 keep**；若 dim9 ≥2 judge 一致显著降（≤ −2）或 dim7/dim4/dim3 任一 ≥2 judge 一致显著为负（≤ −1），触发 Task 5。**Tie-break（v3-C2）**：若 2 judge 在某重点 dim 方向相反（一正一负），spawn 第 3 个独立 judge（同 blind 协议），按多数方向判——round-2 改动涉 negation/dim9 框架冲突区，方差比 round-1 大，预设此规则防僵局。
  - Expected: 给出 keep / 触发 Task 5 的整合结论 + 依据。

- [ ] Step 4: 追加 results.tsv（Python，9 字段，note 单行）
  - Run: Python 追加一行，字段 = `timestamp \t commit \t handoff \t old_score \t new_score \t status \t dimension \t note \t eval_mode`；每字段 `assert '\t' not in f`；note **单行**用 `;` 分隔多段（禁换行/tab）；`write('\n'.join(lines)+'\n')`；末行列数 = 9。
  - note 记录：`round2 结构去重+中模型校准(PHASE1三清单合一+negation6→1+materiality拆分+三PHASE done判据+锚词)+test补全4→9; within-judge delta per dim 见 commit body; dim7/dim4/dim3/dim9 判定 X; 独立judge盲评full_test; 若 C2 tie-break fired 追加 'tie-break: dim X 方向相反 spawn j3'`。delta 详细数据写 commit message body（不入 tsv），body 骨架：
    ```
    darwin full_test（n=2 独立 judge 盲评 A/B）
    - judge1 per-dim Δ：dim1..dim9 = [Δ 列表，合并成一行]
    - judge2 per-dim Δ：dim1..dim9 = [Δ 列表，合并成一行]
    - 经主 agent 跨 judge 整合：dim7 不降、dim4/dim3/dim9 hold，keep
    ```
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
    | dim7（结构/整体架构） | 直接对应（去重） | 预期升；若降 = **真退化**（删错了/留孤儿）→ 回 Task 1/3 补归属 |
    | dim3（失败模式编码）/ dim9（反例黑名单） | 框架冲突区（darwin 奖励显式表/黑名单，WGS 要删） | 若降 = **框架冲突**（多半来自 F3 删 negation）→ 走 Step 2 桥接 |
    | dim4（视觉检查点） | R3 已修，本轮不动 | 若降 = judge 噪声；除非 ≥2 judge 一致，否则 disregard |
    | dim1/2/5/6/8（与去重间接相关） | 间接 | 若降 = judge 噪声/方差；除非 ≥2 judge 一致，否则 disregard |
  - Expected: 区分真退化 / 框架冲突 / 噪声；真退化回 Task 1/3，框架冲突走 Step 2，噪声 disregard。

- [ ] Step 2: 桥接（仅框架冲突）
  - Change: 若 dim3/dim9 因 F3 删 negation 显著降，用「保留/强化 co-located 守卫（不要路由段 + PHASE 0 🛑 + L112）作真正处理器 + 必要时把 F3 翻正面的某条回退为 negation hard guardrail」桥接（参照 brainstorming `5f54f04` / writing-plans round-2 桥接配方）。**回退首选 L113**（「不从跨会话 memory 工具补造」是 silent-drift 反例，darwin dim9 奖励显式编码；其正面锚已在 PHASE 1 入口，回退为 negation 是叠加 guardrail 不冲突）——**而非 L114**（「弱推断包装强结论」已被 L133 verified/inferred/unknown 区分正面覆盖，回退收益低）。若 dim7 真退化，回 Task 1/3 补归属（不是框架冲突）。
  - Expected: 桥接版就绪，复测 delta 转正/hold。

### Task 6: 收口（feature 分支 + commit + --no-ff merge）

- 目标：在 `handoff-round2` 分支收口，--no-ff merge 回 main。
- 涉及文件：SKILL.md + test-prompts.json + results.tsv（+ .gitignore + 本计划文档）
- 接口契约
  - Consumes：Task 1–5 全通过（darwin keep）
  - Produces：feature 分支 commit + main 上 --no-ff merge
- 验证范围：commit message 说明去重 + 中模型校准 + test 补全 + 零行为变更 + darwin delta；merge 保留评审脉络。

- [ ] Step 0: 分支与计划文档归属
  - Change: 执行开始前先建分支并落计划：`git checkout -b handoff-round2` → `git add docs/plans/2026-07-25-handoff-round2-structural-dedup-implementation-plan.md && git commit -m "docs(plans): handoff round2 结构去重实施计划"`（P2-R4：commit msg 对齐文件名，不带「+中模型校准」——与 writing-plans 样板一致；工作 commit Step 1 保留全 scope 描述）。计划先于改动落盘。
- [ ] Step 1: 暂存与提交（工作改动）
  - Run: `git add plugins/iasi/skills/handoff/SKILL.md plugins/iasi/skills/handoff/test-prompts.json plugins/iasi/skills/handoff/results.tsv plugins/iasi/skills/handoff/.gitignore && git commit`
  - Change: message 如 `handoff: round2 结构去重+中模型校准（PHASE1三清单合一 + negation6→1 + materiality拆分 + 三PHASE done判据 + 锚词 + test补全4→9）`，正文记：PHASE 1 三份同源清单收敛为 ranked+imperative 单清单（删执行顺序段）、negation 按 WGS cure 缩到 1 条 hard guardrail（L112）+ 2 条正面化、materiality 按检索难度轴拆分（L136 泛化规则并回 L39 主定义 / L145+L153 微妙守卫 co-locate 保留）、三 PHASE 加 checkable done 判据、materiality/证据优先/只读/自包含 锚词、test-prompts 4→9 覆盖新结构、零行为变更（Task 3 自检通过）、darwin within-judge delta 结论（per-dim 数据入 body）；footer `Co-Authored-By: Claude <noreply@anthropic.com>`。
  - Expected: commit 成功；`git status` clean。
- [ ] Step 2: --no-ff merge 回 main
  - Run: `git checkout main && git merge --no-ff handoff-round2`（保留评审脉络）。
  - Expected: merge 成功；main 含 round-2 改动。

## 执行纪律

- 开始实现前先复查整份计划；发现缺项、矛盾或锚点失配先修计划。
- Task 1 内按 Step 编号顺序执行（MERGE 必须先于 DELETE，避免中间态孤儿）；定位一律用章节锚点字符串，行号仅作提示。
- 每个 Step 的「改动后验证」必须实际跑，不要跳过。
- 遇到删除后某条规则找不到存活副本（触发条件或动作任一），立即停下补归属，不要留孤儿。
- darwin 实测禁主 agent 自评，必须 spawn 独立 Agent 子 judge；judge blind（不知 A/B、不知重点 dim、自读 rubric、不给 keep/revert）；只信 within-judge delta。
- results.tsv 一律 Python 追加（禁 printf）；note 单行 `;` 分隔。
- 分支：全程在 `handoff-round2`，darwin keep 后才 --no-ff merge main。

## 最终验证

- `wc -l plugins/iasi/skills/handoff/SKILL.md` → 约 150–156 行。
- `grep -nE '^## ' …/SKILL.md` → 章节齐全；无 `建议执行顺序`、无独立 `必须做的证据收集` 段、无 L116 重复句。
- Task 3 的 4 项全 pass（三清单合一后 5 项各一次、negation 存活、L113 memory nuance 入正面锚、materiality 主定义全密度+守卫 co-locate、0 外指孤儿、PHASE 0–3 步骤结构未变）。
- `python3 -c "import json;json.load(open('plugins/iasi/skills/handoff/test-prompts.json'));print('json ok')"` → JSON 合法，约 9 条。
- Task 4：≥2 独立 judge within-judge delta，dim7 不降、dim4/dim3 hold、dim9 预期微降 Δ−1~−2 可接受 → keep。
- `python3 -c "import csv;rows=list(csv.reader(open('plugins/iasi/skills/handoff/results.tsv'),delimiter='\t'));assert all(len(r)==9 for r in rows);print(len(rows[-1]),'fields last row')"` → 末行 9 列。
- `git log --oneline main -3` → 含 handoff-round2 --no-ff merge。

## 审阅 Checkpoint

- 计划正文结束（v1）。请审阅；未获批准不进入实现。
- **darwin baseline 说明**：baseline 即 Task 4 Step 1 的 A 版（HEAD 父提交，167 行 post-07-19-R3 状态），Task 4 Step 2 的 same-judge A/B 评分**已自然含基线**（不需要单独跑）。注意 results.tsv 上一条 80.8(j2)/85.5(j1) 是 **07-19 那批 judge** 的分，与本轮 **新 judge** 不可跨 judge 比较（校准 gap）——不要拿 80.8/85.5 当本轮基线做错误归因，只信 within-judge delta。
- **框架冲突预判**：handoff 失败模式已 co-locate 在触发点（不要路由段 + PHASE 0 🛑 + L112），非集中表；本轮不新建诊断索引表（评审 P2-5 确认判断成立）。F3 删 negation 是唯一可能触发 dim9 框架冲突的点——**dim9 预期微降 Δ−1~−2 可接受**（v3-P2-A：不要做段反例 6→1 留 L112 + 翻 L113-114 为正面，弃用歧义的「5/6」表述），靠保留 L112 + 不要路由段（实测 **6 条**，v3-P1-B 修正 v2 的「7 条」）+ PHASE 0 🛑 桥接；若 ≥2 judge 一致 ≤−2 触发 Task 5，首选回退 L113。
- 若批准，按 Task 1 → 2 → 3 → 4 →（5 条件）→ 6 顺序执行；darwin 结论会在 Task 4 回报。

## 修订记录

- **v3（2026-07-26）**：吸收评审 Agent 第二轮报告（主 agent 全部 grep 复核，非轻信任一 reviewer）。**P1 计数订正三项**：A（Step 2 入口 L55→**L56**，L55 实为空行——v2 off-by-one）/ B（不要路由段 7→**6** 条，实测）/ C（三清单**各 6 条**非 5；「5 项」是主动并 #1 同会话历史 + #2 compact 的决策，**非**「对齐 L66-72 既往」——L66-72 既往亦 6 条）。**C3（最关键）**：Step 2 子顺序 (c)negation↔(d)anchor 互换 → 新序 (a)MERGE→(b)DELETE→(c)立只读锚→(d)删 negation→(e)done；v2 原序删 negation 时只读锚尚未立 = 自造中间态孤儿（正是 P1-R3 想防的）。**C1**：L136 由完全 defer 改**半指针半守卫**（「不拼一句/不改写」inline 留 PHASE 2 压缩点，更合检索难度轴）。**C2**：darwin 2 judge 方向相反时 spawn 第 3 judge（negation/dim9 方差大）。**P2**：A（dim9 弃「5/6」歧义表述，改「不要做段 6→1+翻 2 正面」）/ B（跨会话 memory 工具 inline 定义，GLOSSARY.md 未定义）/ D（PHASE 1 62→63 行）。体量 149-155→150-156。**回怼 P2-C**：硬约束 bullets 实测 L37-41（L36 空行），v2 原引正确；评审该条自相矛盾——同「header 后空行」规律抓出 PHASE1 L55/L56，却对硬约束漏算空行误判 L36-40。两轮 reviewer 在 L55/L56 与 L36/L37 上各错一处，互为印证「行号必须自跑 grep」。
  - **【第三轮评审收尾·3 项小修，全部吸收】**：**N1**（L136「283 字符」实为 UTF-8 **字节数 282**，python3 `len()` 按字符 = **114**，与 L137（93）同量级，**非长句**——铁律：量中文行长度用 python3 `len()` 按字符数，**禁** awk `length()`/`wc -c`（拿的是字节数）；全文「283 字符长句」改「114 字符单行」）/ **N2**（Step 3 预期「−2 行」是 v2 完全 defer 残留 → 改 **0 行**，L136 单行→C1 半指针半守卫仍单行）/ **N3**（Step 2(d) 补 L112 与 (c) 入口锚分工：入口锚=只读总纲，L112=解码型 silent-drift 守卫，一总一分非同义重复，防 darwin dim7 把 build-test 误判冗余）。**C1 偏离第三轮亦批准不回退**（恢复与 GLOSSARY.md 检索难度轴的内部一致，v2 完全 defer 违反自己的轴）。**P2-C 回怼第三轮 reviewer 认错成立**。darwin Task 4 Step 4 note 补「tie-break fired」记录便于复盘。
- **v2（2026-07-25）**：吸收评审 Agent 报告。**P0 全部已核查无误**（锚点 grep 实测全对、零行为丢失核查通过、darwin 协议合规）。吸收 **P1 六项**：R1（L136 体量 −2→−0，目标区间上移 149–155）/ R2（三清单「6 源」→「5 项（含 compact 子注）」，与 L66-72 既往对齐）/ R3（Task 1 Step 2 显式子顺序 (a)-(e)，每步 grep 验存活防中间态孤儿）/ R4（L113「用 memory 补造」指跨会话 memory 工具 ≠ L38「优先于回忆」，PHASE 1 入口正面锚显式覆盖 + 自检 grep）/ R5（judge prompt 改绝对路径）/ R6（dim9 目标 hold→预期微降 Δ−1~−2 可接受，Task 5 回退首选 L113 非 L114）。吸收 **P2 四项**：R1（test-prompts id 实测 [1,2,4,3]）/ R2（L116 是 L40 低密度复述，并入 PHASE 1 done 判据后删）/ R3（PHASE 3 done 判据去三重重叠，改自检 yes/no）/ R4（commit msg 对齐文件名）。P2-5（不建诊断索引表判断）评审确认成立；P2-6（严格模式 framing）并入 PHASE 1 入口锚。
- **v1（2026-07-25）**：基于 `/grill-with-docs` 共识（F1-F7）起草。
