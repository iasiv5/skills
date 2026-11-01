# 插件化分发：单包全量 DSH 插件

本仓 skill 内容原靠 `update.sh` 等脚本拷贝进 `~/.agents/skills/` 等目录使用；DSH 原生支持插件经 `ctx.skills.registerProvider` 注册 bundled skill（rank 600，优先级最低）。决定：在**同仓** `dsh-plugin/` 子目录承载插件 wrapper，npm 包名 **`@iasiv5/dsh-skills`**；构建期把根 `skills/` 同步为 `dsh-plugin/skills/`（临时副本，gitignore 不入库），从该子目录发版；纯 host 插件（无 client bundle），`engines.dsh: ">=0.2.0-0"`。

## Considered Options

- **独立插件仓库**：否——skill 内容与打包分离徒增同步成本，单源在根 `skills/`。
- **每 skill 一个插件包**（baoyu 式）：否——本仓 skill 无差异化编辑器后端，28 个包的发布维护成本不划算。
- **包名 `@iasiv5/skills`**：否——与自研插件家族（`@iasiv5/dsh-surf/skins/quota-watch/obmc-web/skip-browser-auth`）命名一致性优先，包名自证「DSH 插件」身份；仓库名保持 `skills` 不动。

## Consequences

- skill 内容变更必须发版才能到达 DSH 插件用户（版本语义：新增=minor、修订=patch、移除/更名=major，CI 门禁强制）。
- 本地 `~/.agents/skills/` 同名副本（rank 500）会遮蔽插件版，装机机器须清理副本；`update.sh` 流程对 DSH 退役，其他 harness（Claude Code 等）不受影响。
