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

1. 读取文章路径、标题、是否只排版还是要 publish。
2. 只在文章缺少 Markdown 结构时补最小结构标记；不改写内容。
3. 未指定主题时优先用 gallery 预览；指定主题时直接 format。
4. 需要 publish 时，先给用户确认预览，再运行 publish.py。
5. 返回预览目录、标题、字数和 media_id；不要回显 APPSECRET。

## Commands

- 排版：scripts/format.py
- 推送：scripts/publish.py

## Support Resources

- templates/：format.py 使用的 preview 和 gallery HTML 模板
- assets/：publish.py 可用的内置封面占位资源；这不是封面设计或图片处理工作流
- evals/：执行样例和 trigger boundary 用例，供回归检查使用

常用命令、参数和完整工作流见 [references/usage.md](references/usage.md)。
主题清单见 [references/themes.md](references/themes.md)。
接口限制见 [references/wechat-mp-api.md](references/wechat-mp-api.md)。
常见故障见 [references/error-codes.md](references/error-codes.md)。
