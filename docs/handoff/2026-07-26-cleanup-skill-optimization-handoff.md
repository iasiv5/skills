# Handoff：cleanup skill 的 writing-great-skills 优化

> 给新 Claude 会话的交接文档。读完这一份 + 文末列出的几个文件，就能直接接着干，**不需要**本会话的对话记忆。
> 交接日期：2026-07-26　·　交接自：handoff round-2 收尾的会话（handoff 已完工 merge main `812544a`）

## 一句话任务

对本地 `cleanup` skill 做 writing-great-skills 优化（4 个本地 skill 的最后一个）。照搬 brainstorming / writing-plans / handoff 走通的配方，**但有一处关键流程改动（见下方 ⚠️ 头号约束）**。

## ⚠️ 头号约束（本轮与前三轮最大的不同，必读）

**用 writing-plans 写完实施计划之后，在这一步停下来——不要自己起 subagent 去评审计划。** 让用户手动启用一个**外部 agent**评审这份实施计划，评审通过之后再接着往下（落地 → darwin → 桥接 → 收口）。

**为什么**：前三轮（尤其 handoff round-2）主 agent 在写完计划后自己 spawn reviewer subagent，把评审意见吸收成 v2/v3 留在计划文档里。这些内部修订痕迹会**锚定/污染**用户后续手动启用外部 agent 的评审——外部 reviewer 看到一份已经过内部多轮打磨的计划，其判断会被既有修订路径带偏，失去"独立新鲜视角"的价值。所以本轮：**计划写完即停，评审权完全交给用户的外部 agent**。

落到操作上：
- writing-plans 方法论里 PHASE 5（inline 自检）照做——那是主 agent 自己对计划的内部一致性自检（占位符/命名/接口/命令），不算"评审"，可做。
- 但**不要**做配方第 4 步的"spawn reviewer agent"——跳过它。
- 计划写好后，明确告诉用户："实施计划已写好并保存到 `<path>`。按你的要求，我在这里停下，不自起评审。请你手动启用外部 agent 评审；评审通过后告诉我，我再继续落地。"
- 用户反馈外部评审意见后，主 agent 再吸收意见修订计划（这时的修订是被外部 reviewer 驱动的，不是自循环）。

## 背景：iasi-skills 优化总图

仓库 `m` 的 `plugins/iasi/skills/` 有 **4 个本地可改 skill**，正在用 `/writing-great-skills` 方法逐个诊断+优化：

| skill | 进度 |
|---|---|
| brainstorming | ✅ 完工（dedup + darwin 桥接 `5f54f04`，303→246 行；darwin 反超 old） |
| writing-plans | ✅ 完工（round-2 MERGE-before-DELETE 去重 `3455cd7` + merge `98ba477`，227→220 行；darwin 双 judge blind A/B KEEP Δ+3.0） |
| handoff | ✅ 完工（round-2 `e66a8d8`+`812544a`，167→140 行；darwin **3 judge** blind A/B KEEP，dim7 三 judge 一致升、dim9 tie-break→hold） |
| **cleanup** | ⬅️ **本轮目标，最后一个**。已有 07-19 四轮 darwin 驱动（baseline 72.3 → R1-R4 后 **78.5**），现做 WGS 方法论下的正式轮 |

**另外 5 个 skill（grilling / codebase-design / domain-modeling / grill-with-docs / improve-codebase-architecture）由 `update.sh` 从 mattpocock/skills 上游冻结同步，不可改**（下次 `./update.sh` 会冲掉本地修改）。

## cleanup 当前状态（本轮起点）

- 文件：`plugins/iasi/skills/cleanup/SKILL.md`，**264 行**——4 个本地 skill 里**最长**（handoff 167 / writing-plans 220 / brainstorming 246 都比它短），sprawl / sediment 靶点最丰富。
- references（3 个，共 233 行）：`references/agent-paths.md`（86 行，跨 runtime 路径对照）、`references/governance.md`（56 行，规范审计细则）、`references/sync-matrix.md`（91 行，同步面矩阵）。
- test-prompts：**4 条**（偏少，brainstorming 13 / handoff round-2 补到 9）——已知缺口。
- results.tsv 历史：`plugins/iasi/skills/cleanup/results.tsv`——07-19 五行：
  - baseline 72.3（jA=71.5 / jB=73.2，gap 1.7 校准）
  - **R1 `bf700e4`** runtime-gate FAIL→PASS（de-Copilot-lock，与 handoff `ba16533` 同款 fix；dim 持平 72.3，KEEP——gate win 是 binary 必须 fix）
  - **R2 `ceea669`** dim4 +3/+2（4 个用户决策门加视觉标记）72.3→73.9
  - **R3 `dee6e8e`** dim7 +2/+0（分层与横切 counting bug 修：3 层 + 1 横切）73.9→75.1
  - **R4 `5c03690`** dim8 +2/+1（PHASE 0 null-/cleanup handler）75.1→**78.5**，HL-4 stop after 4 validated rounds
- **07-19 轮是 darwin 驱动（不是正式 WGS 方法论轮）**——和 handoff 一样，本轮是 WGS 方法论下的正式诊断+优化轮。
- **judge 标记的 open gaps（跨 R1-R4 未闭合）**：
  - **dim7**：counting bug 已修，但 **redundancy 未 collapse**（judge 意见分歧 + trigger-core 风险，R3 选择不合并）→ 本轮 WGS 去重可能正面处理
  - **dim8**：null-handler 已加但 **cap 在 8**（缺 history-depth spec + 用户不答时的 fallback）→ 本轮可补

### 本会话初扫的 WGS 候选靶点（新会话需 darwin baseline + 严格 WGS 诊断复核，非定论）

cleanup 264 行结构臃肿，初扫以下候选（行号为交接时实测，执行以锚点字符串为准）：

1. **【sprawl，主靶】整体 264 行、章节极多**：何时使用 / 不要路由 / 核心边界 / 硬约束 / 分层与横切 / 触发模型（硬触发·软提醒·反触发）/ 资格门 / 正常 cleanup 流程（PHASE 0·1·1B·2·3·4）/ 强制 cleanup（PHASE F0·F1·F2）/ 反膨胀原则 / 立即执行。多个段落编码同一件事，是 sprawl + duplication 富矿。
2. **【duplication，次靶】触发/资格三处重叠**：`何时使用`（L14-24）+ `触发模型-硬触发`（L91-106）+ `资格门`（L125-137）三处都在讲"何时进 cleanup"。`不要路由到 cleanup`（L26-37）+ `反触发`（L117-124）都在讲"不要路由"。`核心边界`（L39-48）+ `分层与横切`（L63-87）都在讲"cleanup vs handoff vs 正式工件"的分工。用检索难度轴判断哪些可 defer 到 single source、哪些须 co-locate。
3. **【duplication/sediment】反膨胀原则（L251-259）讽刺性自指**：cleanup 自身职责是"让知识越来越干净"，但 SKILL.md 自己是 4 个 skill 里最长的——R1-R4 每轮加结构，可能 sediment。重点查 R1-R4 加的段（强制 cleanup PHASE F0/F1/F2、PHASE 0 null-handler、各种 🔴/🛑）是否仍有 load-bearing 价值。
4. **【dim7 open gap】redundancy 未 collapse**：R3 修了 counting bug 但故意没合并 redundancy（judge 分歧）。本轮 WGS 可重新评估——用检索难度轴 + test-mapped failure mode 判断哪些 redundancy 是 co-located 守卫（留）、哪些是纯重复（删/合并）。
5. **【dim8 open gap】null-handler cap 8**：PHASE 0 的 null-handler（裸 `/cleanup` 推断范围）可补 history-depth spec + 用户不答时的 fallback。
6. **【branch/disclosed】强制 cleanup 段（L222-249）**：是一个 distinct branch（任务未稳定时强制沉淀），可考虑 progressive disclosure（指针化）或 condense。
7. **【test-coverage】test-prompts 仅 4 条**：可像 handoff round-2 那样补到 ~8-10 条（用户本轮倾向一起补——见 handoff round-2 F7 决策，但 cleanup 可独立决定）。

### runtime-neutral 当前状态（先扫确认）

memory（`darwin-iasi-plugin-copilot-lock`）警告 iasi-plugin skill 会**复发** Copilot runtime-lock gate-fail。cleanup 07-19 R1（`bf700e4`）已修（runtime-gate FAIL→PASS）。**本会话扫描**：SKILL.md body 干净（0 Copilot 命中）；`references/agent-paths.md` 有「以 GitHub Copilot 仓库为**示例**」+ 跨 runtime 路径对照表（Claude Code / Cursor / Copilot / Codex）——属 runtime-INCLUSIVE 列举（darwin 例外），**不是 lock-in**。当前干净，但新会话第一步仍按惯例跑 darwin runtime 红灯扫描确认没复发（硬约束 #10）。

## 已验证的优化配方（前 3 个 skill 走通的，照搬——但第 4 步改了）

```
1. 诊断（writing-great-skills rubric）
   读 ~/.claude/skills/writing-great-skills/SKILL.md + GLOSSARY.md，
   按 failure modes（premature completion / duplication / sediment / sprawl / no-op / negation）
   + information hierarchy 逐节诊断 cleanup SKILL.md，产出 ranked findings。
   本会话初扫候选见上方，新会话需独立严格复核 + 跑 darwin baseline 摸真实分数。

2. 对齐（grill-with-docs）
   用 /grill-with-docs（= grilling + domain-modeling）和用户一问一答对齐：
   每个 finding 给"我的推荐答案"，用户拍板。维护 m/GLOSSARY.md 术语 + m/docs/adr/ ADR。
   ⚠️ 维护 GLOSSARY.md / ADR 用 domain-modeling 规则：术语即写即更，ADR 仅当 hard-to-reverse+surprising+real-tradeoff 三全才建。

3. 计划（writing-plans skill 方法论）
   把对齐后的设计写成实施计划，落到 docs/plans/<date>-cleanup-...-implementation-plan.md。
   ⚠️ writing-plans 是项目插件 skill，见下方"硬约束#1"——要"用 writing-plans 方法论"就直接读它的 SKILL.md 手动执行。
   PHASE 5 inline 自检（占位符/命名/接口/命令一致性）照做。

4. ⚠️【本步本轮改动】在这里停下——不要自起 subagent 评审。
   见上方"⚠️ 头号约束"。明确告诉用户计划已就绪、不自起评审、等用户手动外部评审。
   前三轮在这一步 spawn reviewer subagent 吸收意见出 v2/v3——本轮禁。评审权交给用户外部 agent。
   用户反馈外部评审意见后，主 agent 再修订计划（修订由外部 reviewer 驱动，非自循环）。

5. 落地
   feature 分支 → 按 plan 定点编辑 → 自检（存活副本 grep + 孤儿扫描 + 主干 diff 验证）→ commit。

6. darwin full_test 实测
   spawn ≥2 独立 judge agent（Agent 工具）盲评 A/B（改后 vs 改前），within-judge 算 delta。
   若某重点 dim 2 judge 方向相反，spawn 第 3 judge tie-break（handoff round-2 C2 配方）。
   ⚠️ 见下方"darwin 硬约束"。

7. 视情况桥接
   若 darwin 因"框架冲突"（dim3/9 奖励显式表/黑名单 vs WGS 要删）而微降，
   用"诊断索引表（信号→动作→详见指针）+ 保留 co-located 守卫"桥接，再 darwin 复测。
```

## 硬约束 / 踩过的坑（新会话必读，省大量时间）

1. **项目插件 skill 不能用 Skill 工具调用**。`cleanup`/`handoff`/`brainstorming`/`writing-plans` 在 `plugins/iasi/skills/`，**未注册到 Skill 工具**（`Skill({skill:"cleanup"})` 会报 Unknown skill）。user-level skill（`~/.claude/skills/` 下的 writing-great-skills / darwin-skill / grilling / grill-with-docs / domain-modeling）才能用 Skill 工具。要"用 writing-plans 方法论写计划"→**直接读它的 SKILL.md 然后手动执行**。

2. **⚠️ 本轮新增：计划写完不要自起评审 subagent**。配方第 4 步已改：写完计划即停，让用户手动启用外部 agent 评审。前三轮自起 reviewer 把意见吸收成 v2/v3 留在计划里，会锚定/污染用户后续的外部评审。inline 自检（PHASE 5）可做，外部评审不可自起。

3. **darwin 跨 judge 总分不可比**（memory: darwin-judge-calibration-gap）。只信 **within-judge delta**：每个 judge 同时评 old+new 两版，算 Δ。绝对总分因 judge 宽严差异可差 ±8 分但 delta 一致。所以 darwin 评估必须是 **blind A/B 同评两版**。judge **不得被告知** A/B 身份、不得被告知"重点 dim 是哪些"、不得输出 keep/revert（keep/revert 由主 agent 跨 judge 整合）。

4. **darwin 自评反模式**（darwin-skill 反例黑名单 #1）：禁同 context 自评自改。dim8 实测必须 spawn **独立 Agent 子 judge**，不能主 agent 自己评。

5. **darwin tie-break（handoff round-2 C2 配方）**：若 ≥2 judge 在某重点 dim 方向相反（一正一负），spawn 第 3 个独立 judge（同 blind 协议），按多数方向判。cleanup 改动若涉 negation/dim9 框架冲突区，方差会比 round-1 大，预设此规则防僵局。handoff round-2 实际触发过（dim9 j1 −1 vs j2 +0.5，spawn j3=0 → 多数非负 hold）。

6. **results.tsv 追加的 tab 陷阱**：用 `printf` 会把内容里的 `%` 当格式符吞掉；且文件末行可能无尾换行导致拼接。**一律用 Python 追加**：`'\t'.join([9字段])`，每个字段 `assert '\t' not in f and '\n' not in f`，`write('\n'.join(lines)+'\n')`。末行列数必须 =9。note 字段**单行**用 `;` 分隔（禁换行/tab），delta 详细数据写 commit body。

7. **⚠️ 量中文行长度用 python3 `len()` 按字符，禁 awk `length()`/`wc -c`**（memory: measure-cjk-length-python-len-not-bytes）。它们返回 UTF-8 **字节数**，CJK 一字≈3 字节，会把普通行误判成"长句"——handoff round-2 的"L136 是 283 字符长句"论证骗了主 agent + 两轮 reviewer 三轮，实测字符数 114（282 是字节），根本不是长句。任何"这行 N 字符""该折行"的论证落笔前用 python3 `len()` 核。

8. **PNG 渲染不可用**（memory: darwin-card-no-png-render）。本 WSL 无 playwright/chromium，darwin 结果卡**交付 HTML 文件**（浏览器打开），不要尝试 screenshot.mjs/PNG。结果记 results.tsv 才是持久记录。

9. **中模型校准**（memory: calibrate-skills-to-mid-model）：用户跑 mid-tier 模型。skill 要的是**压缩锚词**（高密度）不是散文复述（膨胀注意力）。强化 completion criteria + leading word。

10. **检索难度轴**（GLOSSARY.md 术语，brainstorming/writing-plans/handoff 结晶）：salvage 一条规则按"中模型情境里能否检索到"分两类——**微妙情境守卫**（silent drift、跨轮矛盾）须 co-locate 到触发点 PHASE + leading-word 锚 + 配测试；**泛化结构规则**直接 defer 到正面 single source。前台化 vs 去重，由检索难度决定。handoff round-2 的 materiality 拆分（L136 半指针半守卫）正是用这条：泛化规则 defer 回主定义、微妙守卫 inline 留触发点。

11. **框架冲突已知名**：darwin dim3（失败模式编码）/dim9（反例黑名单）/dim5（模板具象）**奖励"有显式失败表+黑名单+脚手架"**；writing-great-skills 把这些判为 duplication/negation/sprawl 要删。两框架意见相反。**桥接解法**：诊断索引表（信号→一线动作→详见指针，不重述正文）+ 保留 co-located 守卫作真正处理器。handoff round-2 的 N3 分工说明（入口锚总纲 vs L112 解码型 silent-drift 守卫）成功守住 dim9——删 negation 时给保留的那条加"为什么不是冗余"的分工注，防 darwin dim7 误扣。

12. **分支策略**：每个 skill 优化开 feature 分支（如 `cleanup-round2`），`--no-ff` merge main 保留评审脉络。commit footer 沿用仓库惯例 `Co-Authored-By: Claude <noreply@anthropic.com>`。

13. **runtime-lock 复发警惕**（memory: darwin-iasi-plugin-copilot-lock）：iasi-plugin skill 会复发 Copilot runtime-lock gate-fail。**每个 skill 优化第一步先跑 darwin runtime 红灯扫描**（`grep -nE '(在 Claude Code|Claude Code skill|Cursor only|Codex 中|~/\.claude/skills)' SKILL.md references/*.md`）。cleanup 当前干净（R1 `bf700e4` 已修，agent-paths.md 是 INCLUSIVE 示例+对照表），但别假设——先扫。注意区分 lock-in（FAIL）vs runtime-INCLUSIVE 列举（PASS，darwin 例外）。

## 新会话建议的第一步

1. 读本文件 + `plugins/iasi/skills/cleanup/SKILL.md` + `~/.claude/skills/writing-great-skills/SKILL.md` + GLOSSARY.md。
2. 跑 darwin runtime 红灯扫描确认 cleanup 当前 runtime-neutral 干净（硬约束 #13）。
3. （可选但推荐）跑一次 darwin full_test baseline 摸 cleanup 当前真实分数（应 ≈ 78.5，但那是 07-19 的 judge 分，不可跨 judge 比较——只作 within-judge A 版用）。
4. 按 writing-great-skills 严格诊断 cleanup（264 行），重点看整体 sprawl（候选#1）+ 触发/资格三处重叠（#2）+ 反膨胀自指（#3）+ dim7 redundancy（#4）+ 任何新发现。
5. 进 grill-with-docs 和用户对齐（一问一答，每问给推荐答案）。
6. 用 writing-plans 方法论写实施计划。
7. **⚠️ 计划写完即停**，告诉用户"不自起评审，等你手动外部评审"，等用户反馈。
8. 用户反馈外部评审意见后，吸收意见修订计划，再继续落地 → darwin → 桥接 → 收口。

## 关键文件指针

| 用途 | 路径 |
|---|---|
| 目标 skill | `plugins/iasi/skills/cleanup/SKILL.md`（264 行，最长） |
| cleanup references | `references/agent-paths.md`（86）/ `governance.md`（56）/ `sync-matrix.md`（91） |
| cleanup 测试 | `test-prompts.json`（4 条，偏少） |
| cleanup 历史 | `results.tsv`（07-19 baseline 72.3 → R1-R4 后 78.5，5 行） |
| 诊断 rubric | `~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md` |
| darwin 评分器 | `~/.claude/skills/darwin-skill/SKILL.md` |
| grill 工具链 | `~/.claude/skills/grill-with-docs/`（= grilling + domain-modeling） |
| 参照成品（最新） | `plugins/iasi/skills/handoff/SKILL.md`（140 行，round-2 半指针半守卫 + N3 分工样板）+ `plugins/iasi/skills/writing-plans/SKILL.md`（220 行，MERGE-before-DELETE + 红灯索引表样板）+ `plugins/iasi/skills/brainstorming/SKILL.md`（246 行，桥接样板） |
| 领域术语 | `GLOSSARY.md`（设计轨道/单向 pull handoff/reviewer gate/test-mapped failure mode/中模型校准/检索难度轴） |
| 架构决策 | `docs/adr/0001-two-track-design-pull-only-plan-handoff.md` |
| 计划样板（最新） | `docs/plans/2026-07-25-handoff-round2-structural-dedup-implementation-plan.md`（经 3 轮评审，含 darwin judge prompt 模板、C2 tie-break、MERGE-before-DELETE、框架冲突判据表） |
| 本 handoff | `docs/handoff/2026-07-26-cleanup-skill-optimization-handoff.md` |

## 领域词汇表（GLOSSARY.md 现有术语，复用不要重造）

设计轨道 (design track) · 单向 pull handoff · reviewer gate · test-mapped failure mode · 中模型校准 · 检索难度轴 (retrieval-difficulty axis)。

## 给新会话的开场提示（可直接发给新 Claude）

> 读 `docs/handoff/2026-07-26-cleanup-skill-optimization-handoff.md`，开始 cleanup skill 优化：先跑 runtime 红灯扫描，再按 writing-great-skills 诊断，然后用 /grill-with-docs 和我对齐细节，用 writing-plans 写实施计划——**写完计划停下不要自起评审 subagent，让我手动启用外部 agent 评审，通过后再继续**。注意 handoff 里"硬约束"那一节列的 13 个坑，尤其 #2（不自起评审）和 #7（量中文行长度用 python3 len）。
