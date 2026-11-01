# NOTICE — 第三方归属与许可汇总

本包（`@iasiv5/dsh-skills`）按 as-is 原则收录 iasiv5/skills 仓库的 28 个 agent skill，其中 20 个来自上游第三方，8 个为本地自研。各 skill 目录内的原许可文件原样保留；本文件汇总归属与许可状态。发版前许可核查记录见仓库维护者的审计档案（2026-11）。

## 🚫 Anthropic 专有（禁止再分发 — 见注记）

- **docx** — anthropics/skills（`skills/docx`）。© 2025 Anthropic, PBC。`LICENSE.txt` 随目录分发，其 ADDITIONAL RESTRICTIONS 禁止向任何第三方分发、提取、复制或演绎。**注记：本包对该材料的收录未经 Anthropic 明示许可；如您不是 Anthropic 服务的授权用户，请勿使用本包中的该 skill，并请改用 Anthropic 官方渠道获取。**
- **pdf** — anthropics/skills（`skills/pdf`）。同上。
- **xlsx** — anthropics/skills（`skills/xlsx`）。同上。

## ⚠️ 上游未声明许可

- **remotion-best-practices** — remotion-dev/skills（`skills/remotion-best-practices`）。上游仓库与目录均未附许可文本，默认版权保留。收录状态待上游明确或经包维护者裁决。

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
