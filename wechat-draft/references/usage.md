# Usage

{skill_dir} 表示本 skill 目录的绝对路径。

## 前置条件

首次使用时：

```bash
cp {skill_dir}/config.example.json {skill_dir}/config.json
pip install -r {skill_dir}/requirements.txt
```

推送前需要在 config.json 中填写公众号凭据：

- wechat.app_id
- wechat.app_secret

纯排版可不填凭据；publish 到 draft 时必需。

## 工作流一：排版并推送

适用场景：用户明确要推草稿，或说“排版后发到公众号草稿箱”。

1. 读取文章路径，确认标题和字数。
2. 如果 Markdown 结构过弱，只补最小标记，比如标题、段落、列表、加粗；不改写内容。
3. 如果需要更强的版式表达，可以在不改字面的前提下补容器语法，比如 :::dialogue、:::gallery、:::timeline、:::steps。
4. 未指定主题时，用 gallery 模式先预览；指定主题时直接排版。
5. 告知用户预览路径，等待确认满意后再 publish。

推荐命令：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink
```

用户已指定主题时：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --theme newspaper
```

确认后推送：

```bash
python3 {skill_dir}/scripts/publish.py \
  --dir "排版输出目录"
```

如果用户已经明确了主题，也可以一步到位：

```bash
python3 {skill_dir}/scripts/publish.py \
  --input "文章路径.md" \
  --theme newspaper
```

完成后应返回：

- 预览输出目录
- 标题和字数
- 草稿 media_id
- 公众号后台入口 https://mp.weixin.qq.com

## 工作流二：只排版

适用场景：用户只要公众号样式预览，不要求 publish。

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --theme newspaper
```

默认告知用户打开输出目录中的 preview.html 查看效果；如果脚本没有自动打开浏览器，再把终端里的 file:/// 路径交给用户。

## 工作流三：配置与故障排查

适用场景：publish 失败或配置未完成。

优先检查：

- config.json 是否存在
- app_id / app_secret 是否正确
- 当前 IP 是否在公众号白名单
- 是否为有草稿接口权限的认证服务号
- token 是否触发频控

错误码和接口限制分别见 [references/error-codes.md](references/error-codes.md) 和 [references/wechat-mp-api.md](references/wechat-mp-api.md)。

## 参数摘要

format.py：

- --input / -i：Markdown 文件，必填
- --theme / -t：直接指定主题
- --output / -o：输出目录
- --no-open：不自动打开浏览器
- --gallery：主题画廊模式
- --recommend：gallery 中高亮推荐主题
- --format：wechat、html、plain

publish.py：

- --dir / -d：已有排版输出目录
- --input / -i：Markdown 文件，自动排版后推送
- --title / -t：文章标题
- --theme：仅在 --input 模式下生效
- --author / -a：作者名
- --dry-run：只排版，不推送

## 操作约束

- 不要回显 APPSECRET。
- 不要手写 HTML 或 CSS 替代脚本。
- 不要承诺自动处理封面图、配图或图片上传。
- 不要承诺列出或管理现有草稿；当前 skill 只负责创建草稿。