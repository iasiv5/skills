# iasiv5/skills

𝓲-Collection：iasiv5 的 Agent Skills 合集。面向 Claude Code、Codex、DeepSeek Harness 等多种 harness 的可复用任务技能（每个 skill 一个目录，`SKILL.md` + 随附脚本/资产）。

## 在 DeepSeek Harness（DSH）中使用

推荐以 DSH 插件方式安装（免拷贝、随版本更新）：

```bash
dsh plugin --profile web add @iasiv5/dsh-skills
```

桌面端在 Plugins 页按名安装 `@iasiv5/dsh-skills`；dsh-m 市场收录后亦可从市场一键安装。安装后重启宿主、**新开会话**生效。详见 [`dsh-plugin/README.md`](./dsh-plugin/README.md)。

> 插件 skill 的优先级低于 workspace 内 `.dsh/skills/`、`.agents/skills/` 的同名副本——若之前用下方脚本安装过，请清理副本后再用插件版。

## 其他 harness（传统方式）

`./update.sh` 从 GitHub 拉取 `.your-skill-collection.json` 声明的上游 skill 覆盖更新（旧版备份到 `.backup/`）。**注意：该流不适用于 DSH**——DSH 用户请走上面的插件安装。

- `local` 列表（本地自研源头）与 `skip` 列表中的 skill 不参与更新。

## 目录约定

- 每个 skill 一个根级目录，入口 `SKILL.md`（YAML frontmatter：`name`/`description`/可选 `whenToUse`/`disable-model-invocation`/`user-invocable`）。
- `Geek-skills-*` 目录名仅是收藏来源标记，实际 skill 名以 frontmatter `name` 为准（如 `keqian-method`）。
- `docs/`（ADR/计划/handoff）为仓库自身文档，不属于任何 skill。
- 上游来源与子目录映射见 `.your-skill-collection.json`；许可归属见 [`dsh-plugin/NOTICE.md`](./dsh-plugin/NOTICE.md)。
- 术语与设计决策：[GLOSSARY.md](./GLOSSARY.md)、`docs/adr/`。
