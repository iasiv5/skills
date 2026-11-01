# @iasiv5/dsh-skills

DeepSeek Harness 插件：把 [iasiv5/skills](https://github.com/iasiv5/skills) 仓库的 skill 合集以 **bundled skill** 方式注册进 DSH 宿主 skill 注册表——安装插件即用，**不再需要**把 skill 拷贝进 `.agents/skills/` 或 `.dsh/skills/`。

## 安装

```bash
dsh plugin --profile web add @iasiv5/dsh-skills
```

或 DSH 桌面/网页端 Plugins 页按名安装（dsh-m 市场收录后可直接从市场装）。安装后**重启宿主并新开会话**生效。

## 使用

- skill 经宿主 skill 注册表统一暴露：模型按情境自动触发（`modelInvocable`），或 `/` 斜杠手动调用（`userInvocable`）。
- 部分 skill 带 `disable-model-invocation: true`（仅斜杠可调），与目录安装行为一致。
- workspace 内 `.dsh/skills/`、`.agents/skills/` 的同名副本优先级**高于**本插件（rank 100–500 vs bundled 600）——要用插件版，请清理本地同名副本。

## 内容与许可

- skill 清单：见仓库根 README；本包按 as-is 收录（不裁剪上游文件）。
- 许可归属：见 [NOTICE.md](./NOTICE.md)——注意 Anthropic 系（docx/pdf/xlsx）上游许可禁止再分发，相关条目附使用注记。

## 更新

仓库内容变更后由维护者发新版；`dshm upgrade`（或插件页更新）+ 重启 + 新会话生效。本地副本不会自动跟随本包更新。
