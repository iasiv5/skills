# Handoff：writing-plans skill 第二轮优化

> 给新 Claude 会话的交接文档。读完这一份 + 文末列出的几个文件，就能直接接着干，**不需要**上一个会话的对话记忆。
> 交接日期：2026-07-25　·　交接自：brainstorming 优化全程的会话

## 一句话任务

对本地 `writing-plans` skill 做**第二轮** writing-great-skills 优化，照搬 brainstorming 走通的配方（诊断 → grill 对齐 → 计划 → 评审 → 落地 → darwin 实测 → 视情况桥接）。

## 背景：iasi-skills 优化总图

仓库 `m` 的 `plugins/iasi/skills/` 有 **4 个本地可改 skill**，正在用 `/writing-great-skills` 方法逐个诊断+优化：

| skill | 进度 |
|---|---|
| brainstorming | ✅ 完工（dedup `a741026` + darwin 桥接 `5f54f04`，303→246 行；darwin full_test 实测反超 old） |
| **writing-plans** | ⬅️ **本轮目标**。已有数轮（最近 `e76bbdb` @07-25），现在做第二轮 |
| handoff | 未开始 |
| cleanup | 未开始 |

**另外 5 个 skill（grilling / codebase-design / domain-modeling / grill-with-docs / improve-code-architecture）由 `update.sh` 从 mattpocock/skills 上游冻结同步，不可改**（下次 `./update.sh` 会冲掉本地修改）。

## writing-plans 当前状态（round-2 起点）

- 文件：`plugins/iasi/skills/writing-plans/SKILL.md`，**227 行**。
- references：`plan-template.md`、`task-skeleton.md`、`plan-self-review.md`（task-skeleton 曾有 40 行 dup 块，R1 `e16abfb` 已修）。
- test-prompts：**仅 5 条**（brainstorming 有 13 条——这是个缺口，round-2 可补）。
- results.tsv 历史：`plugins/iasi/skills/writing-plans/results.tsv`（dry 89.1→91.0 → 独立重评 89.0 → R1/R2 dedup 84→85 judge → 07-25 `e76bbdb` 67.1→66）。

### results.tsv 已标注的 3 个 round-2 靶点（2026-07-25 条目明列，PRE-EXISTING）

1. **dim3 两段式 fallback gap**：writing-plans 的红灯段是"信号→动作"两段；而 darwin HL-2 技法 + brainstorming 桥接后是"触发/一线/仍失败兜底"**三段式**。升级成三段式可拉 dim3。
2. **dim7 STOP 轻度重叠**：🛑 STOP 规则段与"红灯与反例"段有 light overlap，可再 dedup。
3. **dim9 黑名单比 brainstorming 薄**：writing-plans 反例覆盖不如 brainstorming（13 条），可补 test-mapped 反例。

## 已验证的优化配方（brainstorming 走通的，照搬）

```
1. 诊断（writing-great-skills rubric）
   读 ~/.claude/skills/writing-great-skills/SKILL.md + GLOSSARY.md，
   按 failure modes（premature completion / duplication / sediment / sprawl / no-op / negation）
   + information hierarchy 逐节诊断 writing-plans SKILL.md，产出 ranked findings。

2. 对齐（grill-with-docs）
   用 /grill-with-docs（= grilling + domain-modeling）和用户一问一答对齐：
   每个 finding 给"我的推荐答案"，用户拍板。维护 m/GLOSSARY.md 术语 + m/docs/adr/ ADR。
   ⚠️ 维护 GLOSSARY.md / ADR 用 domain-modeling 规则：术语即写即更，ADR 仅当 hard-to-reverse+surprising+real-tradeoff 三全才建。

3. 计划（writing-plans skill 方法论）
   把对齐后的设计写成实施计划，落到 docs/plans/<date>-<feature>-implementation-plan.md。
   ⚠️ writing-plans 是项目插件 skill，见下方"硬约束#1"。

4. 评审（可选但强烈推荐）
   把计划交给一个 reviewer agent（独立 context）审，吸收 B/I/N 类意见、实证验证修复。
   brainstorming 这轮过 3 轮 review 抓出多个真 bug（孤儿指针、awk range bug、正则鲁棒性）。

5. 落地
   feature 分支 → 按 plan 定点编辑 → 自检（PHASE 主干 diff 验证一行不动 + 孤儿扫描 + 存活副本 grep）→ commit。

6. darwin full_test 实测
   spawn ≥2 独立 judge agent（Agent 工具）盲评 A/B（改后 vs 改前），within-judge 算 delta。
   ⚠️ 见下方"darwin 硬约束"。

7. 视情况桥接
   若 darwin 总分因"框架冲突"（dim3/9 奖励显式表/黑名单 vs WGS 要删）而微降，
   用"诊断索引表（信号→动作→详见指针）+ 保留 co-located 守卫"桥接，再 darwin 复测。
```

## 硬约束 / 踩过的坑（新会话必读，省大量时间）

1. **项目插件 skill 不能用 Skill 工具调用**。`writing-plans`/`brainstorming`/`handoff`/`cleanup` 在 `plugins/iasi/skills/`，**未注册到 Skill 工具**（`Skill({skill:"writing-plans"})` 会报 Unknown skill）。user-level skill（`~/.claude/skills/` 下的 writing-great-skills / darwin-skill / grilling / grill-with-docs / domain-modeling）才能用 Skill 工具。要"用 writing-plans 方法论"→**直接读它的 SKILL.md 然后手动执行**。

2. **darwin 跨 judge 总分不可比**（memory: darwin-judge-calibration-gap）。只信 **within-judge delta**：每个 judge 同时评 old+new 两版，算 Δ。绝对总分因 judge 宽严差异可差 ±8 分但 delta 一致。所以 darwin 评估必须是 **blind A/B 同评两版**，不是分别打总分再比。

3. **darwin 自评反模式**（darwin-skill 反例黑名单 #1）：禁同 context 自评自改。dim8 实测必须 spawn **独立 Agent 子 judge**，不能主 agent 自己评。

4. **results.tsv 追加的 tab 陷阱**：用 `printf` 会把内容里的 `%`（如 "20%"）当格式符吞掉；且文件末行可能无尾换行导致拼接。**一律用 Python 追加**：`'\t'.join([9字段])`，每个字段 `assert '\t' not in f`，`write('\n'.join(lines)+'\n')`。末行列数必须 =9。

5. **PNG 渲染不可用**（memory: darwin-card-no-png-render）。本 WSL 无 playwright/chromium，darwin 结果卡**交付 HTML 文件**（浏览器打开），不要尝试 screenshot.mjs/PNG。（注：一次性 HTML 卡用户可能觉得没必要会删，像 brainstorming 那次 `ccd1b60`——结果记 results.tsv 才是持久记录。）

6. **中模型校准**（memory: calibrate-skills-to-mid-model）：用户跑 mid-tier 模型。skill 要的是**压缩锚词**（高密度）不是散文复述（膨胀注意力）。强化 completion criteria + leading word。

7. **检索难度轴**（GLOSSARY.md 术语，brainstorming 这轮结晶）：salvage 规则按"中模型情境里能否检索到"分两类——**微妙情境守卫**（silent-drift 类，情境需先识别再检索）须 co-locate 到触发点 PHASE + leading-word 锚 + 配测试用例；**泛化结构规则**直接 defer 到正面 single source。前台化 vs 去重，由检索难度决定。

8. **分支策略**：每个 skill 优化开 feature 分支（如 `writing-plans-round2`），`--no-ff` merge main 保留评审脉络。main 上既有约定是直推 main（e76bbdb 等），但本地自主大规模重构倾向先分支。

9. **框架冲突已知名**：darwin dim3（失败模式编码）/dim9（反例黑名单）/dim5（模板具象）**奖励"有显式失败表+黑名单+脚手架"**；writing-great-skills 把这些判为 duplication/negation/sprawl 要删。两框架意见相反。**桥接解法**：诊断索引表（信号→一线动作→详见指针，不重述正文）+ 保留 co-located 守卫作真正处理器。brainstorming 桥接后 darwin 反超 old（83.5 vs 77.9）。

## 新会话建议的第一步

1. 读本文件 + `plugins/iasi/skills/writing-plans/SKILL.md` + `~/.claude/skills/writing-great-skills/SKILL.md`。
2. （可选但推荐）先跑一次 darwin full_test baseline 摸 writing-plans 当前真实分数 + 验证那 3 个 flagged 靶点：spawn 3 独立 judge 盲评 current vs 上一个 commit（`e76bbdb` 的父），within-judge delta。
3. 按 writing-great-skills 诊断 writing-plans，重点看 results.tsv 已标的 dim3/dim7/dim9 + 任何新发现的 duplication/sediment。
4. 进 grill-with-docs 和用户对齐（一问一答，每问给推荐答案）。
5. 后续照配方 3-7。

## 关键文件指针

| 用途 | 路径 |
|---|---|
| 目标 skill | `plugins/iasi/skills/writing-plans/SKILL.md`（227 行） |
| writing-plans 测试 | `plugins/iasi/skills/writing-plans/test-prompts.json`（5 条，偏少） |
| writing-plans 历史 | `plugins/iasi/skills/writing-plans/results.tsv` |
| 诊断 rubric | `~/.claude/skills/writing-great-skills/SKILL.md` + `GLOSSARY.md` |
| darwin 评分器 | `~/.claude/skills/darwin-skill/SKILL.md` |
| grill 工具链 | `~/.claude/skills/grill-with-docs/`（= grilling + domain-modeling） |
| 参照成品 | `plugins/iasi/skills/brainstorming/SKILL.md`（246 行，已优化+桥接的样板） |
| 领域术语 | `GLOSSARY.md` |
| 架构决策 | `docs/adr/0001-two-track-design-pull-only-plan-handoff.md` |
| brainstorming 计划样板 | `docs/plans/2026-07-25-brainstorming-structural-dedup-implementation-plan.md` |
| 本 handoff | `docs/handoff/2026-07-25-writing-plans-round2-handoff.md` |

## 领域词汇表（GLOSSARY.md 现有术语，复用不要重造）

设计轨道 (design track) · 单向 pull handoff · reviewer gate · test-mapped failure mode · 中模型校准 · 检索难度轴。

## 给新会话的开场提示（可直接发给新 Claude）

> 读 `docs/handoff/2026-07-25-writing-plans-round2-handoff.md`，然后开始 writing-plans 第二轮优化：先按 writing-great-skills 诊断，再用 /grill-with-docs 和我对齐细节，再出计划。注意 handoff 里"硬约束"那一节列的 9 个坑。
