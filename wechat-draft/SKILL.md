---
name: wechat-draft
description: "公众号文章排版并推送到草稿箱。Markdown → 微信兼容 HTML → 草稿箱。仅当用户明确要将文章推送到公众号草稿箱时使用：例如提到推草稿、发草稿、推公众号、草稿箱、draft、推送到公众号、排版并推送。也覆盖纯排版场景：排版、公众号排版、微信排版、选主题、预览主题。不用于：写文章内容、图片/封面处理、润色改写文章。图片和封面由用户自行处理。"
---

# wechat-draft

公众号一键排版并推送到草稿箱。把 Markdown 文章转为微信兼容的内联样式 HTML，预览确认后推送到公众号草稿箱。

## 能力边界

- 排版：`scripts/format.py` — Markdown → 微信兼容 HTML（30 主题、CJK 排版、容器语法）
- 推送：`scripts/publish.py` — HTML → 公众号草稿箱
- 不处理图片和封面（用户自行处理）
- 不写文章内容、不润色改写

`{skill_dir}` 表示本 skill 目录的绝对路径。

## 前置条件

首次使用需配置：

```bash
# 1. 复制配置模板
cp {skill_dir}/config.example.json {skill_dir}/config.json

# 2. 安装依赖
pip install -r {skill_dir}/requirements.txt

# 3. 编辑 config.json，填写公众号凭据
#    wechat.app_id — 公众号开发者 AppID
#    wechat.app_secret — 公众号开发者 AppSecret
```

纯排版可不填 wechat 凭据，推送时必需。

## Claude 该做什么

### 工作流一：排版 + 推送（完整流程）

用户说「排版并推到草稿箱」「推公众号」等：

**第 1 步：读取文章**
- 用户给文件路径直接读取，没给则询问
- 确认标题和字数

**第 2 步：结构化预处理（仅在需要时）**
- 检测 Markdown 格式标记数量（`##` 标题、`**加粗**`、`- 列表` 等）
- 格式充分 → 跳过
- 纯文本/粗糙笔记 → 补标题、分段、加粗、列表（不改内容，只加标记）

**第 3 步：AI 内容增强**
- 分析内容类型，自动套用容器语法：
  - 对话/访谈 → `:::dialogue[标题]`
  - 连续多图 → `:::gallery[标题]`
  - 核心观点 → `> [!important]` / `> [!tip]`
  - 章节转换处 → `---`
- 增强后保存为临时文件

**第 4 步：推荐主题**

| 内容类型 | 推荐主题 |
|----------|----------|
| 深度长文/分析 | newspaper, magazine, ink |
| 科技产品/AI | bytedance, github, sspai |
| 访谈/对话 | terracotta, coffee-house, mint-fresh |
| 教程/指南 | github, sspai, bytedance |
| 文艺/随笔 | terracotta, sunset-amber, lavender-dream |

**第 5 步：排版预览**

默认用 Gallery 模式让用户选主题：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink
```

用户指定主题时直接排版：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --theme newspaper
```

**第 6 步：确认并推送**

告诉用户排版结果（标题、字数），让用户确认效果满意。

用户确认后，给**配图和封面建议**（文字建议，不处理图片）：

- 建议在哪些段落间插入配图
- 封面图风格建议

用户说「推吧」时执行推送：

```bash
python3 {skill_dir}/scripts/publish.py \
  --dir "排版输出目录"
```

或一步到位：

```bash
python3 {skill_dir}/scripts/publish.py \
  --input "文章路径.md" \
  --theme newspaper
```

推送成功后提示：
- 草稿 media_id
- 公众号后台地址：https://mp.weixin.qq.com → 草稿箱查看
- 提醒用户在后台补充封面图后再发布

### 工作流二：只排版

用户说「排版这篇文章」但不提推送：

```bash
python3 {skill_dir}/scripts/format.py \
  --input "文章.md" --theme newspaper
```

只生成预览，不推送草稿箱。

### 工作流三：一步到位

用户说「把 article.md 推到草稿箱」且已确认主题：

```bash
python3 {skill_dir}/scripts/publish.py \
  --input article.md --theme newspaper
```

自动排版 + 推送。

## Claude 不该做什么

- 不要手写 HTML 或内联 CSS 替代 format.py
- 不要重写文章内容（只允许补结构标记）
- 不要声称会自动识别所有容器（需要 Claude 分析内容后手动套用）
- 不要处理图片上传和封面生成（这是用户的事）
- 不要把 APPSECRET 回显到终端输出

## 可用主题（30 个）

### 独立风格（9 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 赤陶 | terracotta | 暖橙色，左边框渐变 |
| 字节蓝 | bytedance | 蓝青渐变，科技现代 |
| 中国风 | chinese | 朱砂红，古典雅致 |
| 报纸 | newspaper | 纽约时报风，严肃深度 |
| GitHub | github | 开发者风，浅色代码块 |
| 少数派 | sspai | 中文科技媒体红 |
| 包豪斯 | bauhaus | 红蓝黄三原色 |
| 墨韵 | ink | 纯黑水墨，极简留白 |
| 暗夜 | midnight | 深色底+霓虹色 |

### 精选风格（7 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 运动 | sports | 渐变色带，活力动感 |
| 薄荷 | mint-fresh | 薄荷绿，清爽健康 |
| 日落 | sunset-amber | 琥珀暖调 |
| 薰衣草 | lavender-dream | 紫色梦幻 |
| 咖啡 | coffee-house | 棕色暖调 |
| 微信原生 | wechat-native | 微信绿 |
| 杂志 | magazine | 超大留白，品质长文 |

### 模板系列（14 个）

四种布局（简约/聚焦/精致/醒目）× 多种配色

## 内置排版增强

- CJK 间距修复：中英文/中数字间自动加空格
- 加粗标点修复：`**文字，**` → `**文字**，`
- 纯内联样式：所有 CSS 直接写在 `style="..."`
- 列表模拟：`<ul>/<ol>` → flexbox
- 外链转脚注：`[text](url)` → 正文 `text[1]` + 文末脚注
- 多类型提示框：`[!tip]`/`[!important]`/`[!warning]` 各有独立配色
- 对话气泡：`:::dialogue[标题]`
- 图片画廊：`:::gallery[标题]`
- 时间线：`:::timeline[标题]`
- 步骤展示：`:::steps[标题]`
- 对比卡片：`:::compare[A vs B]`
- 引用块：`:::quote[作者]`
- 暗色模式支持

## 参数说明

**format.py**：
- `--input` / `-i`：Markdown 文件（必须）
- `--gallery`：主题画廊模式（推荐）
- `--theme` / `-t`：直接指定主题
- `--output` / `-o`：输出目录
- `--recommend`：推荐主题（gallery 中高亮）
- `--no-open`：不自动打开浏览器
- `--format`：wechat/html/plain

**publish.py**：
- `--dir` / `-d`：排版输出目录
- `--input` / `-i`：Markdown 文件（自动排版再推送）
- `--title` / `-t`：文章标题
- `--theme`：排版主题（仅 --input 模式）
- `--author` / `-a`：作者名
- `--dry-run`：只排版不推送

## 错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| config.json 不存在 | 首次使用 | `cp config.example.json config.json` |
| APPID/APPSECRET 无效 | 配置错误 | 检查公众号后台 → 开发者配置 |
| IP 不在白名单 | 安全限制 | 公众号后台 → IP 白名单添加当前 IP |
| API 未授权 | 权限不足 | 需认证服务号，开通草稿接口 |
| token 获取超频 | 日限额 | 每日 2000 次，稍后重试 |
