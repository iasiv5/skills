---
name: wechat-draft
description: "把【现成】Markdown 文章排版成微信兼容 HTML、选主题预览、确认后推送到公众号草稿箱。输入必须是一篇已成稿的文章，本 skill 不创作内容。触发词：公众号排版、微信排版、Markdown 转微信、选主题、预览主题、推草稿、publish to draft。明确不做、请改用其他 skill：写/创作公众号文章 → Geek-skills-wechat-article-writer；把文章转成幻灯片 → note-slides；做公众号封面/小红书图 → guizang-social-card-skill；润色/rewrite/配图上传/草稿箱管理 也都不在本 skill 范围。"
---

# wechat-draft

把现成 Markdown 文章转换为微信兼容 HTML，确认预览后推送到公众号草稿箱。

## Mode

Production。入口保留路由和执行骨架；详细参数见 references/。

## Owns / Does Not Own

**Owns**：Markdown→微信HTML排版 / theme preview+gallery / 确认后 draft 推送 / config+凭据+IP白名单排障
**Does Not Own**：写/改/润色文章 / 配图/封面图/图片 / 草稿箱管理 / 手写 HTML 替代 format.py

## Trigger Guide

✅ 排版公众号样式 / 选主题 / 推草稿 / 排查推送配置
❌ 写文章/润色 / 封面图/配图 / 管理草稿

## Execution Skeleton

### 步骤 1：读取输入

读取文章路径、标题、用户意图（只排版 or 排版+推送）。

| 如果 | 则 |
|------|-----|
| 文件不存在 / 非 .md | 确认路径拼写或提示仅支持 Markdown |
| 文件为空 | 提醒内容过少，继续排版但标注 |

### 步骤 2：预处理

检查文章是否有基本 Markdown 结构。**"缺少结构"的判断标准**：
- 无标题（缺少 `#` / `##`）→ 补 `# {首行文本}`
- 无段落分隔（全文一整块）→ 在空行处插入 `\n\n`
- 关键词但无强调 → 无需处理（不改内容）

**禁止改写内容**——结构混乱需要大改时，告知用户先整理后再排版。

| 如果 | 则 |
|------|-----|
| 文件已是标准 Markdown（有标题/段落/列表） | 跳过预处理，直接进步骤 3 |
| 文件几乎无结构（纯文本无标记） | 补标题+段落分隔，告知用户"已补最小结构" |

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

- templates/、assets/、evals/、config.example.json：模板、资源、测试用例；首次使用**必须** `cp config.example.json config.json`
- 文档：[usage.md](references/usage.md) · [themes.md](references/themes.md) · [wechat-mp-api.md](references/wechat-mp-api.md) · [error-codes.md](references/error-codes.md)

## 操作黑名单（严格禁止）

| 禁止 | 正确做法 |
|------|----------|
| 改写文章内容 | 建议用户先完成内容后再排版 |
| 回显 APPSECRET | 不显示或只显示 app_id 前4位 |
| 手写 HTML 替代 format.py | 必须通过 format.py 生成 |
| 未确认预览就推送 | 🔴 等用户确认预览满意 |
| 处理封面图/配图/管理草稿 | 封面和草稿管理在公众号后台操作 |
| 跳过前置检查直接 publish | 推送前必须检查 config + IP 白名单 |
| 跳过 format 直接 publish | 必须先通过 format.py 生成 HTML 再推送 |
