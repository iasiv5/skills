---
name: wechat-draft
description: "公众号 Markdown 排版与 draft 推送。用于把现成文章 format 成微信兼容 HTML、提供 theme preview，并在用户明确要求 publish 时推送到公众号草稿箱。触发包括：公众号排版、微信排版、选主题、预览主题、推草稿、publish to draft。仅处理排版、preview、draft 推送和配置排障；不用于写文章、rewrite、润色、封面图、配图上传或列出草稿。"
---

# wechat-draft

把现成 Markdown 文章转换为微信兼容 HTML，并在用户确认预览后推送到公众号草稿箱。

## Mode

Production。这个 skill 会被重复使用，而且与写稿、润色、图片处理和草稿管理等近邻请求容易混淆，所以入口只保留路由、边界和执行骨架。

## Owns

- Markdown 到微信兼容 HTML 的排版
- theme preview、gallery 选主题、指定主题直出
- 用户确认后的 draft 推送
- config.json、凭据、IP 白名单、token 频控相关排障

## Does Not Own

- 写文章、改写、润色、扩写
- 配图、封面图、图片上传或生成
- 草稿箱查询、列出、删除、编辑
- 手写 HTML 或内联 CSS 替代 scripts/format.py

## Trigger Guide

Use this skill when the user:

- 明确要把现成文章排版成公众号样式
- 提到 theme、preview、gallery、newspaper、terracotta 等主题选择
- 明确要 push / publish 到公众号 draft
- 需要排查 publish 到草稿箱的配置问题

Do not use this skill when the user:

- 主要诉求是写文章内容或改写文案
- 主要诉求是封面图、配图、素材处理
- 想查看或管理现有草稿

## Execution Skeleton

### 步骤 1：读取输入

读取文章路径、标题、用户意图（只排版 or 排版+推送）。

**失败分支**：
| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| 文件路径不存在 | 向用户确认路径是否有拼写错误 | 让用户提供正确路径再继续 |
| 文件非 Markdown 格式 | 询问是否需要先转换为 .md | 告知仅支持 Markdown 输入 |
| 文件为空或只有标题 | 提醒用户文章内容过少 | 继续排版但标注"内容过少" |

### 步骤 2：预处理（只补结构，不改内容）

只在文章缺少 Markdown 结构时补最小标记（标题、段落、列表、加粗）。
**禁止改写内容**——如果发现文章结构混乱需要大改，告知用户"建议先整理内容再排版"。

### 步骤 3：选择主题并排版

- 用户指定主题 → 直接 `format.py --input <path> --theme <name>` 排版
- 用户未指定主题 → **必须**用 gallery 模式：`format.py --input <path> --gallery --recommend newspaper,magazine,ink`
- 推荐主题对照：深度长文 → newspaper/magazine/ink；科技产品 → bytedance/github/sspai；访谈对话 → terracotta/coffee-house/mint-fresh

完整 30 个主题清单见 [references/themes.md](references/themes.md)。

**失败分支**：
| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| format.py 报 ModuleNotFoundError | 运行 `pip install -r requirements.txt` | 提示用户检查 Python 环境 |
| format.py 报其他运行时错误 | 检查输入文件编码是否为 UTF-8 | 将完整错误信息发给用户排查 |
| 用户对 gallery 结果不满意 | 按内容类型推荐备选主题 | 让用户指定 `--theme` 参数手动选择 |

### 步骤 4：预览确认

告知用户预览路径（`output/<article-name>-<timestamp>/preview.html`），让用户在浏览器中打开查看。

🔴 **CHECKPOINT · 🛑 STOP：用户未确认"预览满意"前，禁止执行 publish。**

### 步骤 5：推送草稿（仅在用户明确要求时执行）

用户确认预览后，运行 `publish.py --dir <排版输出目录>`。

**推送前检查**：
- config.json 存在且 app_id / app_secret 已填写
- 当前 IP 在公众号白名单内
- 公众号为认证服务号（有草稿接口权限）

**失败分支**：
| 触发条件 | 一线修复 | 仍失败兜底 |
|----------|----------|------------|
| config.json 不存在 | 运行 `cp config.example.json config.json` 并提示填写凭据 | 引导用户阅读 usage.md 前置条件 |
| 报错 40001/40125（凭据无效） | 检查 app_id/app_secret 是否正确 | 提示到公众号后台重置 AppSecret |
| 报错 40164（IP 白名单） | 引导到公众号后台 → 设置 → IP 白名单添加当前 IP | 详见 [references/error-codes.md](references/error-codes.md) |
| 报错 48001（API 未授权） | 告知需认证服务号才有草稿权限 | 建议用户确认公众号类型 |

推送成功后返回：预览目录路径、文章标题、字数、media_id（草稿 ID）、公众号后台入口 https://mp.weixin.qq.com。

**🔴 禁止回显 APPSECRET。**

### 步骤 6：排障（故障场景专用）

当用户报告排版或推送错误时，按以下优先级排查：

1. config.json 是否存在且凭据正确
2. Python 依赖是否完整（`pip install -r requirements.txt`）
3. 输入文件是否为有效 Markdown
4. 当前 IP 是否在公众号白名单
5. 是否触发 API 频控（每日 token 获取上限 2000 次）

详细错误码见 [references/error-codes.md](references/error-codes.md)。

## Commands

- 排版：`scripts/format.py --input <path> --theme <name> [--gallery] [--recommend t1,t2] [--output <dir>] [--no-open]`
- 推送：`scripts/publish.py --dir <排版输出目录> | --input <path> --theme <name> [--dry-run]`
- 完整参数说明见 [references/usage.md](references/usage.md)

## Support Resources

- templates/：preview 和 gallery HTML 模板
- assets/：内置封面占位资源（非封面设计工作流）
- evals/：执行样例和 trigger boundary 用例
- config.example.json：配置模板，首次使用必须复制为 config.json

常用命令和完整工作流见 [references/usage.md](references/usage.md)。
主题清单见 [references/themes.md](references/themes.md)。
接口限制见 [references/wechat-mp-api.md](references/wechat-mp-api.md)。
常见故障见 [references/error-codes.md](references/error-codes.md)。

## 操作反例黑名单

以下操作**严格禁止**，即使被用户暗示要求也不要做：

| # | 禁止操作 | 理由 | 正确做法 |
|---|----------|------|----------|
| 1 | 改写文章内容 | 本 skill 只排版不改稿 | 建议用户先完成内容后再排版 |
| 2 | 回显 APPSECRET | 凭据泄露风险 | 只显示 `app_id 前4位...` 或不显示 |
| 3 | 手写 HTML/CSS 替代 format.py | 会产生不兼容输出 | 必须通过 format.py 生成 |
| 4 | 未确认预览就推送 | 可能发布错误内容到公众号 | 🔴 必须等用户确认预览满意 |
| 5 | 处理封面图/配图 | 不在本 skill 范围 | 告知用户封面应在公众号后台上传 |
| 6 | 管理现有草稿 | 本 skill 只负责创建草稿 | 列出/删除草稿请直接在公众号后台操作 |
| 7 | 跳过前置检查直接 publish | 常导致 40164/48001 报错 | 推送前必须检查 config + IP 白名单 + 公众号权限 |
