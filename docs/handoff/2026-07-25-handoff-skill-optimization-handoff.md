# Handoff：handoff skill 的 writing-great-skills 优化

> 给新 Claude 会话的交接文档。读完这一份 + 文末列出的几个文件，就能直接接着干，**不需要**本会话的对话记忆。
> 交接日期：2026-07-25　·　交接自：writing-plans round-2 收尾的会话

## 一句话任务

对本地 `handoff` skill 做 writing-great-skills 优化，照搬 brainstorming / writing-plans 走通的配方（诊断 → grill 对齐 → 计划 → 评审 → 落地 → darwin 实测 → 视情况桥接）。

## 背景：iasi-skills 优化总图

仓库 `m` 的 `plugins/iasi/skills/` 有 **4 个本地可改 skill**，正在用 `/writing-great-skills` 方法逐个诊断+优化：

| skill | 进度 |
|---|---|
| brainstorming | ✅ 完工（dedup + darwin 桥接 `5f54f04`，303→246 行；darwin 反超 old） |
| writing-plans | ✅ 完工（round-2 MERGE-before-DELETE 去重 `3455cd7` + merge `98ba477`，227→220 行；darwin 双 judge blind A/B KEEP Δ+3.0，dim7 +1.0/+1.5） |
| **handoff** | ⬅️ **本轮目标**。已有 07-19 一轮（baseline 68.3 → 80.8/85.5），现做 WGS 方法论下的下一轮 |
| cleanup | 未开始（最后一个） |

**另外 5 个 skill（grilling / codebase-design / domain-modeling / grill-with-docs / improve-code-architecture）由 `update.sh` 从 mattpocock/skills 上游冻结同步，不可改**（下次 `./update.sh` 会冲掉本地修改）。

## handoff 当前状态（本轮起点）

- 文件：`plugins/iasi/skills/handoff/SKILL.md`，**167 行**。
- references：`references/handoff-output-template.md`（固定输出模板，含骨架+预算+硬规则）。
- agents：`agents/interface.yaml`（runtime adapter 配置，openai/claude/generic 三向）。
- test-prompts：**仅 4 条**（happy-path / boundary-recap / boundary-low-content / explicit-goal-drives-materiality）——偏少（brainstorming 13、writing-plans 5），是已知缺口。
- results.tsv 历史：`plugins/iasi/skills/handoff/results.tsv`——07-19 baseline 68.3 → R1+R2+R3 后 **80.8(j2)/85.5(j1)** KEEP。R1 runtime-neutral（修 Copilot-lock 渗出）、R2 materiality 3x→1 + 合并 P1/P2 问题清单、R3 🔴/🛑 视觉标记上 PHASE 0 gate。baseline 最弱维度原为 dim4=5（无视觉检查点）、dim7=6（materiality 3x + P1/P2 问题清单 ~80% 重复），R1-R3 已大幅修这两维。

### 本会话初扫的 WGS 候选靶点（新会话需 darwin baseline + 严格 WGS 诊断复核，非定论）

1. **【dim7/sprawl，主靶】PHASE 1 占 62 行（L54-116），内部有近逐项重复**：`证据优先级`(L58-64) 与 `建议执行顺序`(L81-87) 是**同一组 6 个证据源**（同会话历史/compact/可见对话/todo/git/文件）的两份清单，仅 git 在执行顺序里拆成 diff-stat + status。执行顺序没增加优先级清单没有的信息 → 合并为一份（按优先级即顺序），或删执行顺序清单、留优先级清单 + "按上面优先级顺序执行"一句。
2. **【dim7/duplication，次靶】materiality + verbatim + 只读规则散落**：materiality 出现在 SKILL.md L39（硬约束，主定义）/L136（PHASE2 沿用+加 nuance）/L145（PHASE2 二次复核）/L153（PHASE3 三次筛选）+ template L5/L20/L66，共 7 处。⚠️ 注意：L39/L145/L153 是"初次/二次/三次 materiality"的**有意三阶段 co-location**（每阶段在其触发点提醒），不一定是纯重复——用 `检索难度轴` 判断哪些是可 defer 到 single source 的泛化规则、哪些是须 co-locate 的守卫。只读约束散落 7 处（硬约束 L37 主定义 + PHASE1 L55/63/70/71/74/87），L55 "仅使用只读动作"重述 L37。
3. **【negation，低优先】PHASE 1「不要做这些事」(L108-114)**：6 条 negation（编辑文件/创建文件/改 git/跑 install-build-test/用 memory 补造/弱推断包装强结论）。按 WGS negation，硬 guardrail（不改文件/不改 git）可留 negation，其余可翻正。R1-R3 未碰这块。
4. **【test-coverage，可选延后】test-prompts 仅 4 条**：覆盖缺口，可像 writing-plans round-2 那样本轮延后、留独立轮补。

### runtime-neutral 当前状态（先扫确认）

memory（`darwin-iasi-plugin-copilot-lock`）警告 iasi-plugin skill 会**复发** Copilot runtime-lock gate-fail。但 07-19 R1 已修（results.tsv 记 "runtime-neutral, Copilot lock bled into output, gate issue"）。本会话扫描：SKILL.md L9 与 template L115 的 "GitHub Copilot Chat、Claude Code、Cursor 等" 是 **runtime-INCLUSIVE 列举**（举多个 runtime 为例），属 darwin 例外，不是 lock-in。**当前干净**，但新会话第一步仍按惯例跑 darwin runtime 红灯扫描确认没复发。

## 已验证的优化配方（brainstorming + writing-plans 走通的，照搬）

```
1. 诊断（writing-great-skills rubric）
   读 ~/.claude/skills/writing-great-skills/SKILL.md + GLOSSARY.md，
   按 failure modes（premature completion / duplication / sediment / sprawl / no-op / negation）
   + information hierarchy 逐节诊断 handoff SKILL.md，产出 ranked findings。
   本会话初扫候选见上方，新会话需独立严格复核。

2. 对齐（grill-with-docs）
   用 /grill-with-docs（= grilling + domain-modeling）和用户一问一答对齐：
   每个 finding 给"我的推荐答案"，用户拍板。维护 m/GLOSSARY.md 术语 + m/docs/adr/ ADR。
   ⚠️ 维护 GLOSSARY.md / ADR 用 domain-modeling 规则：术语即写即更，ADR 仅当 hard-to-reverse+surprising+real-tradeoff 三全才建。

3. 计划（writing-plans skill 方法论）
   把对齐后的设计写成实施计划，落到 docs/plans/<date>-<feature>-implementation-plan.md。
   ⚠️ writing-plans 是项目插件 skill，见下方"硬约束#1"——要"用 writing-plans 方法论"就直接读它的 SKILL.md 手动执行。

4. 评审（强烈推荐）
   把计划交给一个 reviewer agent（独立 context）审，吸收 B/I/N 类意见、实证验证修复。
   writing-plans round-2 过 3 轮 review 抓出真坑（MERGE-before-DELETE 防孤儿、darwin blind 规范、行号核对）。

5. 落地
   feature 分支 → 按 plan 定点编辑 → 自检（存活副本 grep + 孤儿扫描 + 主干 diff 验证）→ commit。

6. darwin full_test 实测
   spawn ≥2 独立 judge agent（Agent 工具）盲评 A/B（改后 vs 改前），within-judge 算 delta。
   ⚠️ 见下方"darwin 硬约束"。

7. 视情况桥接
   若 darwin 总分因"框架冲突"（dim3/9 奖励显式表/黑名单 vs WGS 要删）而微降，
   用"诊断索引表（信号→动作→详见指针）+ 保留 co-located 守卫"桥接，再 darwin 复测。
```

## 硬约束 / 踩过的坑（新会话必读，省大量时间）

1. **项目插件 skill 不能用 Skill 工具调用**。`handoff`/`brainstorming`/`writing-plans`/`cleanup` 在 `plugins/iasi/skills/`，**未注册到 Skill 工具**（`Skill({skill:"handoff"})` 会报 Unknown skill）。user-level skill（`~/.claude/skills/` 下的 writing-great-skills / darwin-skill / grilling / grill-with-docs / domain-modeling）才能用 Skill 工具。要"用 writing-plans 方法论写计划"→**直接读它的 SKILL.md 然后手动执行**。

2. **darwin 跨 judge 总分不可比**（memory: darwin-judge-calibration-gap）。只信 **within-judge delta**：每个 judge 同时评 old+new 两版，算 Δ。绝对总分因 judge 宽严差异可差 ±8 分但 delta 一致。所以 darwin 评估必须是 **blind A/B 同评两版**，不是分别打总分再比。judge **不得被告知** A/B 身份、不得被告知"重点 dim 是哪些"、不得输出 keep/revert（keep/revert 由主 agent 跨 judge 整合）。

3. **darwin 自评反模式**（darwin-skill 反例黑名单 #1）：禁同 context 自评自改。dim8 实测必须 spawn **独立 Agent 子 judge**，不能主 agent 自己评。

4. **results.tsv 追加的 tab 陷阱**：用 `printf` 会把内容里的 `%` 当格式符吞掉；且文件末行可能无尾换行导致拼接。**一律用 Python 追加**：`'\t'.join([9字段])`，每个字段 `assert '\t' not in f and '\n' not in f`，`write('\n'.join(lines)+'\n')`。末行列数必须 =9。note 字段**单行**用 `;` 分隔（禁换行/tab），delta 详细数据写 commit body。

5. **PNG 渲染不可用**（memory: darwin-card-no-png-render）。本 WSL 无 playwright/chromium，darwin 结果卡**交付 HTML 文件**（浏览器打开），不要尝试 screenshot.mjs/PNG。结果记 results.tsv 才是持久记录（一次性 HTML 卡用户可能觉得没必要会删，像 brainstorming 那次 `ccd1b60`）。

6. **中模型校准**（memory: calibrate-skills-to-mid-model）：用户跑 mid-tier 模型。skill 要的是**压缩锚词**（高密度）不是散文复述（膨胀注意力）。强化 completion criteria + leading word。

7. **检索难度轴**（GLOSSARY.md 术语，brainstorming/writing-plans 结晶）：salvage 一条规则按"中模型情境里能否检索到"分两类——**微妙情境守卫**须 co-locate 到触发点 PHASE + leading-word 锚 + 配测试；**泛化结构规则**直接 defer 到正面 single source。前台化 vs 去重，由检索难度决定。handoff 的 materiality 三阶段正是用这条判断的难点。

8. **分支策略**：每个 skill 优化开 feature 分支（如 `handoff-optimization`），`--no-ff` merge main 保留评审脉络。

9. **框架冲突已知名**：darwin dim3（失败模式编码）/dim9（反例黑名单）/dim5（模板具象）**奖励"有显式失败表+黑名单+脚手架"**；writing-great-skills 把这些判为 duplication/negation/sprawl 要删。两框架意见相反。**桥接解法**：诊断索引表（信号→一线动作→详见指针，不重述正文）+ 保留 co-located 守卫作真正处理器。writing-plans round-2 即用此法（红灯段→索引表 + 删冗余 STOP 段，darwin Δ+3.0）。

10. **runtime-lock 复发警惕**（memory: darwin-iasi-plugin-copilot-lock）：iasi-plugin skill 会复发 Copilot runtime-lock gate-fail。**每个 skill 优化第一步先跑 darwin runtime 红灯扫描**（`grep -nE '(在 Claude Code|Claude Code skill|Cursor only|Codex 中|~/\.claude/skills)' SKILL.md README.md`）。handoff 当前干净（R1 已修），但别假设——先扫。修复是 copy-paste 从已修的 handoff/writing-plans。

## 新会话建议的第一步

1. 读本文件 + `plugins/iasi/skills/handoff/SKILL.md` + `~/.claude/skills/writing-great-skills/SKILL.md` + GLOSSARY.md。
2. 跑 darwin runtime 红灯扫描确认 handoff 当前 runtime-neutral 干净（硬约束 #10）。
3. （可选但推荐）跑一次 darwin full_test baseline 摸 handoff 当前真实分数 + 验证上方候选靶点：spawn ≥2 独立 judge 盲评 current vs 07-19 R3 后的 commit，within-judge delta。
4. 按 writing-great-skills 严格诊断 handoff，重点看 PHASE 1 内部重复（候选#1）+ materiality/只读散落（#2）+ 任何新发现。
5. 进 grill-with-docs 和用户对齐（一问一答，每问给推荐答案；materiality 三阶段是重点对齐项——哪些 co-locate、哪些 defer）。
6. 后续照配方 3-7。

## 关键文件指针

| 用途 | 路径 |
|---|---|
| 目标 skill | `plugins/iasi/skills/handoff/SKILL.md`（167 行） |
| handoff 输出模板 | `plugins/iasi/skills/handoff/references/handoff-output-template.md` |
| handoff adapter | `plugins/iasi/skills/handoff/agents/interface.yaml` |
| handoff 测试 | `plugins/iasi/skills/handoff/test-prompts.json`（4 条，偏少） |
| handoff 历史 | `plugins/iasi/skills/handoff/results.tsv`（07-19 baseline 68.3 → 80.8/85.5） |
| 诊断 rubric | `~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md` |
| darwin 评分器 | `~/.claude/skills/darwin-skill/SKILL.md` |
| grill 工具链 | `~/.claude/skills/grill-with-docs/`（= grilling + domain-modeling） |
| 参照成品（最新） | `plugins/iasi/skills/writing-plans/SKILL.md`（220 行，round-2 MERGE-before-DELETE 去重的样板）+ `plugins/iasi/skills/brainstorming/SKILL.md`（246 行，桥接样板） |
| 领域术语 | `GLOSSARY.md`（设计轨道/单向 pull handoff/reviewer gate/test-mapped failure mode/中模型校准/检索难度轴） |
| 架构决策 | `docs/adr/0001-two-track-design-pull-only-plan-handoff.md` |
| writing-plans round-2 计划样板 | `docs/plans/2026-07-25-writing-plans-round2-structural-dedup-implementation-plan.md`（经三轮评审，含 darwin judge prompt 模板、MERGE-before-DELETE 模式） |
| 本 handoff | `docs/handoff/2026-07-25-handoff-skill-optimization-handoff.md` |

## 领域词汇表（GLOSSARY.md 现有术语，复用不要重造）

设计轨道 (design track) · 单向 pull handoff · reviewer gate · test-mapped failure mode · 中模型校准 · 检索难度轴 (retrieval-difficulty axis)。

## 给新会话的开场提示（可直接发给新 Claude）

> 读 `docs/handoff/2026-07-25-handoff-skill-optimization-handoff.md`，开始 handoff skill 优化：先跑 runtime 红灯扫描，再按 writing-great-skills 诊断，然后用 /grill-with-docs 和我对齐细节，再出计划。注意 handoff 里"硬约束"那一节列的 10 个坑。
