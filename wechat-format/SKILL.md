---
name: wechat-format
description: "把 Markdown 或纯文本文章排成微信公众号编辑器可直接粘贴的 HTML 排版 skill。仅当用户明确在做微信公众号图文排版时使用：例如提到微信排版、公众号排版、公众号图文、转成公众号格式、转成微信图文格式、生成可粘贴到公众号后台的 HTML、给公众号文章选主题、预览公众号主题、按某个公众号主题排版。即使用户只说‘把这篇文章排成公众号样式’或‘给这篇公众号文章换个主题’，也应触发。不要用于写公众号文章、润色改写文章、普通 Markdown 美化、网页 HTML/CSS 开发、海报封面生成、草稿推送或评论回复。"
---

# wechat-format

只做一件事：把文章排成适合微信公众号编辑器粘贴的 HTML。

## 能力边界

- 只负责排版、预览和主题选择
- 核心脚本是 `scripts/format.py`
- 不负责推送草稿箱、封面生成、评论回复或任何公众号后台操作

`{skill_dir}` 表示本 skill 目录的绝对路径。执行脚本时要替换成真实路径，不要把占位符原样传给终端。

## Claude 该做什么

- 读取文章，判断是否需要先做最小限度的 Markdown 结构整理
- 在确定会提升可读性时，补少量容器语法，让脚本渲染出更好的公众号效果
- 帮用户推荐主题，默认走画廊模式
- 调用 `format.py` 生成预览页和最终 HTML

## Claude 不该做什么

- 不要手写整篇 HTML 或内联 CSS 来替代 `format.py`
- 不要把原文重写成另一篇文章。只允许补结构，不允许擅自改观点、删信息、加信息
- 不要声称脚本会自动替用户识别并发明所有容器。脚本会渲染你写进 Markdown 的容器语法，但不会替你凭空补剧情
- 不要把“帮我排版”这类泛化表达自动理解成触发；只有上下文明确指向公众号图文排版时才使用本 skill
- 不要把这个 skill 用在发公众号、配封面、评论回复等场景

## 首次使用与前置检查

如果用户是第一次使用，先检查 `config.json` 是否存在。缺失时参考 `config.example.json` 进行配置。

如果是在新环境首次运行，或终端报 `ModuleNotFoundError: No module named 'markdown'`，先安装依赖再继续：

```bash
python3 -m pip install -r "{skill_dir}/requirements.txt"
```

纯排版至少需要：

- `output_dir`
- `settings.default_theme`
- `settings.auto_open_browser`

## 默认排版工作流

### 1. 确认输入

- 用户给了文件路径：直接读取
- 用户只贴了正文：先保存成一个工作用 `.md` 文件，再继续
- 用户没给路径也没贴正文：先要文章内容，不要急着跑脚本

读取后确认标题和字数。`format.py` 会自动从 frontmatter、H1 或文件名提取标题。

### 2. 判断是否需要“最小结构化”

这一步只在源内容很粗糙时使用，比如纯文本、采访速记、没有标题分段的笔记。判断标准要保守：

- 已经有清晰标题、列表、引用、代码块：不要改
- 只是有一点粗糙，但结构还能用：不要改
- 真的是大段纯文本或口语化记录：才做最小结构化

最小结构化的原则：

- 只补 Markdown 结构，不改措辞和信息
- 可以补 `##` 标题、空行、列表、少量 `**强调**`
- 不要硬拆层级，不要把三段内容拆成五个标题
- 保存为工作副本，例如 `xxx-structured.md`，并告诉用户你做了什么

### 3. 只在有把握时做“轻增强”

如果文章本身已经清楚，不需要增强。只有在你能明确判断会带来收益时，才补这些标记：

- 访谈或问答体：用 `:::dialogue[标题]` 包住连续对话
- 3 张以上同组图片：用 `:::gallery[标题]`
- 超长流程图或长截图：用 `:::longimage[标题]`
- 重点观点：用 `> [!important]` 或 `> [!tip]`
- 章节转场：补一个 `---`
- 图片说明：图片后用斜体图说 `*说明文字*`

一篇文章里不要塞太多容器。增强的目标是提高可读性，不是炫技。增强后的工作副本建议保存为 `xxx-enhanced.md`。

### 4. 主题建议

如果用户没指定主题，先给 2-3 个主题建议，再默认打开画廊。可用这张速查表：

| 内容类型 | 推荐主题 |
|----------|----------|
| 深度长文 / 分析 | `newspaper`, `magazine`, `ink` |
| 科技产品 / AI 工具 | `bytedance`, `github`, `sspai` |
| 访谈 / 对话体 | `terracotta`, `coffee-house`, `mint-fresh` |
| 教程 / 操作指南 | `github`, `sspai`, `bytedance` |
| 随笔 / 观点 / 文艺内容 | `terracotta`, `sunset-amber`, `lavender-dream` |
| 快讯 / 活动 / 节奏感强的内容 | `sports`, `bauhaus`, `chinese` |

如果用户已经明确说了主题名，直接用，不要强行改成推荐主题。

### 5. 默认走画廊模式

默认命令：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink
```

重点：画廊模式会用用户的真实文章并行渲染多个主题。在同一浏览器里，页面会记住你上次选过的主题。

### 6. 用户已选主题时走单主题模式

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --theme terracotta
```

常见输出：

- `output_dir/<文章名>/preview.html`：带复制按钮的预览页
- `output_dir/<文章名>/article.html`：实际排版后的 HTML
- `output_dir/<文章名>/images/`：复制出来的本地图片

## 脚本会自动处理什么

这些能力已经在脚本里，不要重复手工做：

- 中英文 / 中数字间距修复
- 加粗标点纠正
- 微信兼容的内联样式注入
- Markdown 链接转脚注
- 普通 Markdown 图片复制
- `> [!tip]`、`> [!important]` 等 callout 渲染
- `:::dialogue`、`:::gallery`、`:::longimage` 渲染
- 单主题预览页与多主题画廊输出

## 容器语法示例

```markdown
:::dialogue[采访摘录]
主持人：你为什么做这个工具？
作者：因为公众号编辑器太难用了。
:::

:::gallery[产品截图]
![](shot-1.png)
![](shot-2.png)
![](shot-3.png)
:::

> [!important] 核心结论
> 这里放文章最值得读者记住的一句话。
```

## 参数速查

`format.py`：

- `--input` / `-i`：输入 Markdown 文件路径，必填
- `--gallery`：打开主题画廊，默认优先使用
- `--theme` / `-t`：直接指定主题
- `--output` / `-o`：输出目录
- `--recommend`：推荐主题 ID，画廊里会高亮
- `--no-open`：不自动打开浏览器
- `--format`：`wechat`、`html`、`plain`

## 处理风格

- 默认少问问题，只问路径、主题偏好这类关键问题
- 先用脚本，再补解释，不要反过来
- 用户只要结果时，优先执行；用户要可控性时，再展示你准备怎么做
- 用户对排版不满意时，优先换主题或减少增强，不要重写原文
