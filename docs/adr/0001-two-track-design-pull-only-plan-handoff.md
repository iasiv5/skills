# ADR 0001：writing-plans 单向 pull 承接两条设计轨道

- 状态：已接受
- 日期：2026-07-25
- 决策者：iasi.hu + Claude（经 `/grill-with-docs` 会话）

## 背景

writing-plans 是实施计划入口。上游有两条把"模糊想法"收敛成可拆计划输入的设计轨道：

- `brainstorming` —— 澄清式（一次一问 → 方案比较 → spec 文档），本地适配、可改。
- `grill-with-docs` —— 对抗式（严苛访谈 + domain-modeling → ADR/glossary），由 `update.sh` 从 mattpocock/skills 上游**冻结同步**，不可本地修改（下次同步会冲掉）。

原 writing-plans 只认"已批准的设计文档"作为输入，且 fallback 只点名 `brainstorming`。后果：

- grill 路径的产出（ADR + CONTEXT + 共识）不是一份 design 文档，会被误判为"设计未定"而弹回 brainstorming。
- grill-with-docs 没有出口指针（上游冻结，无法加），访谈结束后用户不知道下一步该进 writing-plans。

## 决策

1. **单向 pull**：不在冻结的 grill-with-docs 加出口 handoff；改由 writing-plans 识别 grill 产物来承接。
2. **gate**：用户主动转向 planning（自然话术，如"拆计划"）即 gate，不加确认令牌。ADR/CONTEXT 为可选 fuel——盘上有就读，没有就走 writing-plans 现有的"足够清晰需求"分支，不新开分支。
3. **fallback 对等 fork**：设计未就绪时，对等提供三条路：`brainstorming`（比较方案 / 多选澄清）、`grill-with-docs`（对抗式压力测试已有想法）、直接补更清晰需求。权威表述一处，其余简述。

## 后果

- writing-plans 按名引用 `grill-with-docs`（一个冻结上游 skill）——可接受的耦合：skill 名是稳定身份，且对称于 brainstorming↔writing-plans 已有的互相按名引用。
- grill 路径拿不到现成 handoff payload（不像 brainstorming PHASE 8），靠对话 + ADR/CONTEXT 重建 scope / open-items。
- 两条设计轨道在 writing-plans 入口对等，fallback 不再偏袒 brainstorming。

## 考虑过的替代方案

- **在 grill-with-docs 加 push handoff**（镜像 brainstorming PHASE 8）：否决——上游冻结，`update.sh` 下次同步冲掉。
- **要求产物落盘作为 gate**：否决——domain-modeling 懒加载（"only when you have something to write"），很多 grill session 结束时无新 ADR / 术语，会漏掉合法 END。
- **新增加权确认令牌**（如 `共识已固化：<path>`）：否决——"用户主动转向 planning"已是可观测 gate，令牌是多余摩擦；brainstorming 需要令牌是因为"批准文档"本身有歧义，grill→plan 无此歧义。

## 关联

- 同源 glossary 见 `m/GLOSSARY.md`：设计轨道、单向 pull handoff、reviewer gate、test-mapped failure mode、中模型校准。
- 触发本次决策的会话：`/grill-with-docs` 审问 writing-plans 两步重构计划（2026-07-25）。
