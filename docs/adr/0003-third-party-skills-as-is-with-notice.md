# 第三方 skill 全量收录，as-is 分发 + NOTICE

本仓含 7 个第三方 skill（anthropic 系 docx/pdf/xlsx、guizang ×2、darwin-skill、note-slides，另有 Geek ×2 未附 LICENSE 文件）。决定：单包全量收录、**不裁剪任何文件**；逐 skill 保留原 LICENSE，根级 `NOTICE.md` 汇总归属（Geek ×2 如实标注「upstream 未声明许可」），发版前做一轮许可条款核查。依据：这些内容在 GitHub 仓库本已公开托管，npm 包只是同一内容的第二分发通道，不构成增量暴露；裁剪节省的体积不值得引入「包内内容 ≠ 仓内内容」的偏差。

## Consequences

- npm 包体积包含非运行时元文件（CONTRIBUTING/SPONSORS/双语 README 等），接受的代价。
- 构建门禁只做 frontmatter 合法性与重名检测 + 引用完整性冒烟（防手滑删文件），不做裁剪清单。
- 若上游收回许可或提出异议，剔除该 skill 属行为变更，按 major 重发。

## 修订（2026-11-01，发版前许可核查后，主人批示 D4/D5）

许可核查（审计档案 2026-11）推翻了本 ADR 的两个前提，修订如下：

1. **「npm 仅为同内容第二通道」不成立**：anthropic 系 docx/pdf/xlsx 的 LICENSE.txt 明文禁止向第三方分发/提取/复制——npm 打包是主动再分发，直接违约（GitHub 托管的灰色性不能外推到 npm 包）。经主人批示：**docx/pdf/xlsx 剔除出 npm 包**（仓库保留原样），构建脚本以 `PACKAGING_EXCLUDE` 显式排除并打印。
2. **remotion-best-practices 上游无许可**（remotion-dev/skills 404）：同批剔除出包，待上游明确后再议（D5）。
3. **Geek ×2「上游未声明许可」假设修正**：staruhub/ClaudeSkills 仓库级 MIT（© 2025-2026 staruhub）覆盖其子目录，NOTICE 按 MIT 归属收录。
4. 打包集由此 **28 → 24**（18 模型可触发 + 6 仅斜杠）；as-is 原则继续适用于**收录范围内**的 skill 与仓库整体；`PACKAGING_EXCLUDE` 是唯一的许可驱动排除面，新增排除须走主人决策并同步本 ADR。
5. NOTICE.md 相应改写为「收录 + 未收录及缘由」双层结构；首发即排除状态（无版本迁移问题，1.0.0 未发布）。
