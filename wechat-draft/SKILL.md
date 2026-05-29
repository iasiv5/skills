---
name: wechat-draft
description: "公众号 Markdown 排版与 draft 推送。用于把现成文章 format 成微信兼容 HTML、提供 theme preview，并在用户明确要求 publish 时推送到公众号草稿箱。触发包括：公众号排版、微信排版、选主题、预览主题、推草稿、publish to draft。仅处理排版、preview、draft 推送和配置排障；不用于写文章、rewrite、润色、封面图、配图上传或列出草稿。"
---

# wechat-draft

把现成 Markdown 文章转换为微信兼容 HTML，并在用户确认预览后推送到公众号草稿箱。

## Mode

Production。入口保留路由、边界和执行骨架；详细参数和历史版本见 references/。

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

使用：排版成公众号样式 / 选主题(preview/gallery/newspaper/terracotta) / 推草稿(publish to draft) / 排查推送配置
禁用：写文章/改写/润色 / 封面图/配图/素材 / 管理现有草稿

## Execution Skeleton

### 步骤 1：读取输入

读取文章路径、标题、用户意图（只排版 or 排版+推送）。

| 如果 | 则 |
|------|-----|
| 文件不存在 / 非 .md | 确认路径拼写或提示仅支持 Markdown |
| 文件为空 | 提醒内容过少，继续排版但标注 |

### 步骤 2：预处理

只在文章缺少 Markdown 结构时补最小标记（标题/段落/列表/加粗）。**禁止改写内容**——结构混乱需要大改时，告知用户先整理后再排版。

### 步骤 3：选择主题并排版

- 用户指定主题 → `format.py --input <path> --theme <name>`
- 未指定主题 → **必须** gallery：`format.py --input <path> --gallery --recommend newspaper,magazine,ink`
- 主题推荐：深度长文→newspaper/magazine/ink；科技→bytedance/github/sspai；访谈→terracotta/coffee-house/mint-fresh。完整 30 个主题见 [references/themes.md](references/themes.md)。

**如果 format.py 报错**：ModuleNotFoundError → `pip install -r requirements.txt`；其他错误 → 检查文件编码(UTF-8)，仍失败则将报错原文发给用户。
**如果 gallery 结果不满意**：按内容类型推荐备选主题，或让用户 `--theme` 手动指定。

### 步骤 4：预览确认

告知预览路径让用户浏览器打开。🔴 **CHECKPOINT · 🛑 STOP：用户未确认"预览满意"前，禁止执行 publish。**

### 步骤 5：推送草稿（仅在用户明确要求时）

推送前**必须**检查：config.json 存在且凭据已填、IP 在公众号白名单内、认证服务号（有草稿权限）。

| 如果报错 | 修复 |
|----------|------|
| config.json 不存在 | `cp config.example.json config.json` 并提示填凭据 |
| 40001/40125 凭据无效 | 检查 app_id/app_secret，仍失败到公众号后台重置 |
| 40164 IP 白名单 | 公众号后台 → 设置 → IP 白名单添加当前 IP |
| 48001 API 未授权 | 需认证服务号，建议确认公众号类型 |
| 排版/推送其他错误 | 按优先级排查：依赖→编码→Markdown格式→频控(每日2000次) |

推送成功后返回：预览目录、标题、字数、media_id、公众号后台 https://mp.weixin.qq.com。🔴 **禁止回显 APPSECRET**。

## Commands

- 排版：`scripts/format.py --input <path> --theme <name> [--gallery] [--recommend t1,t2] [--output <dir>] [--no-open]`
- 推送：`scripts/publish.py --dir <排版输出目录> | --input <path> --theme <name> [--dry-run]`
- 完整参数说明见 [references/usage.md](references/usage.md)

## Support Resources

- templates/、assets/、evals/：模板、占位资源、测试用例
- config.example.json：首次使用**必须**复制为 config.json
- 详细文档：[usage.md](references/usage.md) · [themes.md](references/themes.md) · [wechat-mp-api.md](references/wechat-mp-api.md) · [error-codes.md](references/error-codes.md)

## 操作黑名单（严格禁止）

| 禁止 | 正确做法 |
|------|----------|
| 改写文章内容 | 建议用户先完成内容后再排版 |
| 回显 APPSECRET | 不显示或只显示 app_id 前4位 |
| 手写 HTML 替代 format.py | 必须通过 format.py 生成 |
| 未确认预览就推送 | 🔴 等用户确认预览满意 |
| 处理封面图/配图/管理草稿 | 封面和草稿管理在公众号后台操作 |
| 跳过前置检查直接 publish | 推送前必须检查 config + IP 白名单 |
