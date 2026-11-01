# 第三方 skill 全量收录，as-is 分发 + NOTICE

本仓含 7 个第三方 skill（anthropic 系 docx/pdf/xlsx、guizang ×2、darwin-skill、note-slides，另有 Geek ×2 未附 LICENSE 文件）。决定：单包全量收录、**不裁剪任何文件**；逐 skill 保留原 LICENSE，根级 `NOTICE.md` 汇总归属（Geek ×2 如实标注「upstream 未声明许可」），发版前做一轮许可条款核查。依据：这些内容在 GitHub 仓库本已公开托管，npm 包只是同一内容的第二分发通道，不构成增量暴露；裁剪节省的体积不值得引入「包内内容 ≠ 仓内内容」的偏差。

## Consequences

- npm 包体积包含非运行时元文件（CONTRIBUTING/SPONSORS/双语 README 等），接受的代价。
- 构建门禁只做 frontmatter 合法性与重名检测 + 引用完整性冒烟（防手滑删文件），不做裁剪清单。
- 若上游收回许可或提出异议，剔除该 skill 属行为变更，按 major 重发。
