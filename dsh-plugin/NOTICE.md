# NOTICE — 第三方归属与许可汇总

本包（`@iasiv5/dsh-skills`）收录 iasiv5/skills 仓库 28 个 agent skill 中的 **24 个**（16 个上游第三方 + 8 个本地自研；18 个模型可自动触发 + 6 个仅斜杠调用）。收录遵循 as-is 原则（不裁剪上游文件）；**4 个 skill 因上游许可不允（或缺失）而被排除在包外**（见下节，仓库内保留）。各收录 skill 目录内的原许可文件原样保留；本文件汇总归属与许可状态。核查方法与逐 skill 台账见维护者审计档案（2026-11）。

## 🚫 未收录：Anthropic 专有（禁止再分发）

以下三个 skill 保留在仓库中，但**未收录于本包**：其上游许可（`LICENSE.txt`，© 2025 Anthropic, PBC）的 ADDITIONAL RESTRICTIONS 明文禁止向任何第三方分发、提取、复制或演绎，npm 打包发布将构成违约再分发。

- **docx** — anthropics/skills（`skills/docx`）
- **pdf** — anthropics/skills（`skills/pdf`）
- **xlsx** — anthropics/skills（`skills/xlsx`）

如您是 Anthropic 服务的授权用户，请直接通过 Anthropic 官方渠道（anthropics/skills 仓库）获取。

## ⚠️ 未收录：上游未声明许可

- **remotion-best-practices** — remotion-dev/skills（`skills/remotion-best-practices`）。上游仓库与目录均未附许可文本，默认版权保留；经维护者裁决暂不收录，待上游明确后再议。

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
