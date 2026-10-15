# Glossary

本仓库（workspace `skills`）的领域模型与术语。决策记录见 `docs/adr/`。

> 单插件阶段，根级 GLOSSARY.md 即可。若 marketplace 长出多个插件、各自有独立决策，改用 `GLOSSARY-MAP.md` 指向各插件子 context。

## 设计轨道 (design track)

上游把"模糊想法"收敛成 writing-plans 可消费输入的方式。本仓两条，**互为对等入口**：

- `brainstorming` —— 澄清式：一次一个问题、方案比较、产出 spec 设计文档。本地适配，可改。
- `grill-with-docs` —— 对抗式：严苛访谈（grilling）+ domain-modeling，产出 ADR 与 glossary。上游冻结同步。

## 单向 pull handoff

下游 skill 靠**识别上游产物**来承接上游，而非依赖上游推送 payload。用于上游冻结、不可本地加出口指针的场景。对照：brainstorming → writing-plans 是协同（有现成 payload）；grill-with-docs → writing-plans 是单向 pull（靠 writing-plans 自己识别 ADR / GLOSSARY）。

## reviewer gate

任务边界判定标准：只有当 reviewer 可以**单独拒绝**某个任务、同时接受相邻任务时，该任务作为独立单元才成立。setup / 配置 / 脚手架 / 文档更新通常并入需要它们的交付任务。

## test-mapped failure mode

skill "反例段"的挑选标准：用已知失败案例（`test-prompts.json`）作为入选依据，每条写成"信号 → 动作"。区别于"补正面规则的漏"——它的价值是前台化最常翻车点供诊断。

## 中模型校准 (mid-model calibration)

按 mid-tier 模型（非 Opus 级）校准 skill 的默认基准：保留**压缩锚词**（高密度、结尾重新 prime）、删**散文式复述**（低密度、膨胀注意力）、强化 completion criteria 与 leading word。中模型跨长文档携带弱、情境 → 规则检索不可靠，因此要的是压缩而非重复。

## 检索难度轴 (retrieval-difficulty axis)

salvage 一条 skill 规则时的判据：按"中模型在情境里能否检索到它"分两类。**微妙情境守卫**（如 silent drift、跨轮矛盾）——情境需先被识别再检索，中模型易漏，须 co-locate 到触发点 PHASE + leading-word 锚，并以测试用例验证；测不过则前台化为"信号 → 动作"。**泛化结构规则**（如多子系统拆分、可视化降级）——情境里易检索，直接 defer 到正面规则 single source 即可，重复才是病。本轴调和 `test-mapped failure mode`（保留信号）与 `中模型校准`（压缩非重复）的张力：要不要前台化重复一条规则，由检索难度决定。
