# NOTICE — 第三方归属与许可汇总

本包（`@iasiv5/dsh-skills`）收录 iasiv5/skills 仓库中的全部 **28 个** agent skill（20 个上游第三方 + 8 个本地自研；19 个模型可自动触发 + 9 个仅斜杠调用）。收录遵循 as-is 原则（不裁剪上游文件）；**1 个 skill 因上游许可缺失而被排除在包外**（见下节）。各收录 skill 目录内的原许可文件原样保留；本文件汇总归属与许可状态。核查方法与逐 skill 台账见维护者审计档案（2026-11）。

## Apache-2.0

- **docx** — anthropics/skills（`skills/docx`）。上游于 2026-11 将原 Anthropic 专有 LICENSE.txt 换为 Apache License 2.0（版权归属行保留上游模板占位 `Copyright [yyyy] [name of copyright owner]`），再分发限制解除；2026-11-08 起收入本包。
- **pdf** — anthropics/skills（`skills/pdf`）。同上。
- **xlsx** — anthropics/skills（`skills/xlsx`）。同上。
- **impeccable** — pbakaus/impeccable（`.dsh/skills/impeccable`，repo LICENSE，Apache-2.0，© Paul Bakaus）。收录上游为 DeepSeek Harness 编译的 `.dsh` 专用构建（SKILL.md 内嵌 DSH 工具名与 `/` 命令语法，子代理角色以 `reference/degraded/` 降级版随包）；2026-11-10 起收入本包。

## ⚠️ 未收录：上游未声明许可

- **remotion-best-practices** — remotion-dev/skills（`skills/remotion-best-practices`）。上游仓库与目录均未附内容许可文本，默认版权保留；经维护者裁决暂不收录，待上游明确后再议。上游 4.0.541 新增的 `remotion-license` 子技能只是 Remotion **软件**商业许可（remotion.pro）的查询指引，不构成对 skill 内容本身的许可授权，故排除维持。

## MIT 许可

- **architecture-diagram** — Cocoon-AI/architecture-diagram-generator（repo LICENSE，MIT）
- **answer-me-with-html** — QingYunA/answer-me-with-html（repo LICENSE，MIT）；内嵌 Bangers 字体受 SIL Open Font License 1.1 约束（`licenses/OFL-Bangers.txt`）
- **darwin-skill** — alchaincyf/darwin-skill（目录内 `LICENSE`，MIT，© 2026 alchaincyf (花叔)）
- **note-slides** — gainubi/note-slides（目录内 `LICENSE`，MIT，© 2026 podcast-notes-slides contributors）
- **grilling / teach / writing-for-agents / grill-with-docs / domain-modeling / codebase-design / retro / improve-codebase-architecture** — mattpocock/skills（repo LICENSE，MIT；本地有适配改动，改动部分随本仓以同源许可精神分发）
- **Geek-skills-keqian-method**（skill 名 `keqian-method`）— staruhub/ClaudeSkills（repo LICENSE，MIT，© 2025-2026 staruhub；上游冻结收录）
- **Geek-skills-xuefeng-method**（skill 名 `xuefeng-method`）— 同上

## AGPL-3.0

- **guizang-ppt-skill** — op7418/guizang-ppt-skill（目录内 `LICENSE`，GNU AGPL-3.0）。逐字收录（未修改）；AGPL 许可证随目录完整分发。
- **guizang-social-card-skill** — op7418/guizang-ppt-skill（目录内 `LICENSE`，GNU AGPL-3.0）。同上。

## 本地自研（iasiv5 仓库维护，无上游归属义务）

brainstorming、cleanup、code-review、eli5、grill-with-docs*、handoff、npm-name-claim、wechat-draft、writing-plans（*grill-with-docs 为 mattpocock 上游冻结同步，已列 MIT 节）

---

各 skill 的上游快照关系与同步方式见仓库 `.your-skill-collection.json` 与 `update.sh`。本包整体不构成上游项目的背书。
