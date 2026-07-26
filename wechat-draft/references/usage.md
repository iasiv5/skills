# Usage

{skill_dir} 表示本 skill 目录的绝对路径。**流程与规则见 SKILL.md 的 Execution Skeleton**；本文只给命令与参数细节。

## 首次配置

```bash
cp {skill_dir}/config.example.json {skill_dir}/config.json
pip install -r {skill_dir}/requirements.txt
```

纯排版可不填凭据；publish 到 draft 需在 config.json 填 `wechat.app_id` / `wechat.app_secret`。

## format.py 参数

| 参数 | 说明 |
|------|------|
| --input / -i | Markdown 文件，必填 |
| --theme / -t | 直接指定主题 |
| --output / -o | 输出目录 |
| --no-open | 不自动打开浏览器 |
| --gallery | 主题画廊模式（预览多个主题） |
| --recommend | gallery 中高亮推荐的主题 ID，**空格分隔**，如 `--recommend newspaper magazine ink` |
| --format | wechat / html / plain |

示例：

```bash
# 画廊模式预览，高亮推荐
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink

# 指定主题直接排版
python3 {skill_dir}/scripts/format.py \
  --input "文章路径.md" \
  --theme newspaper
```

## 容器语法（format.py 扩展，不改字面）

需要更强版式表达时，可在 Markdown 里补这些容器块（`:::类型[标题]` 开头，`:::` 结尾），format.py 会渲染成对应版式：

| 容器 | 命令 | 用途 |
|------|------|------|
| 对话气泡 | `:::dialogue` | 问答/访谈 |
| 图片画廊 | `:::gallery` | 横向滚动多图 |
| 长图 | `:::longimage` | 单张长图说明 |
| 数据统计 | `:::stat` | 关键数字/指标 |
| 时间线 | `:::timeline` | 事件序列 |
| 步骤 | `:::steps` | 教程/流程 |
| 对比 | `:::compare` | A vs B |
| 引用 | `:::quote` | 重点摘录 |

## publish.py 参数

| 参数 | 说明 |
|------|------|
| --dir / -d | 已有排版输出目录 |
| --input / -i | Markdown 文件，自动排版后推送 |
| --title / -t | 文章标题 |
| --theme | 仅 --input 模式下生效 |
| --author / -a | 作者名 |
| --dry-run | 只排版，不推送 |

示例：

```bash
# 排版输出目录直接推
python3 {skill_dir}/scripts/publish.py --dir "排版输出目录"

# 从 Markdown 一步到位（需指定主题）
python3 {skill_dir}/scripts/publish.py \
  --input "文章路径.md" \
  --theme newspaper
```

## 排障 checklist

publish 失败时按序检查：

1. config.json 是否存在、app_id / app_secret 是否正确
2. 当前 IP 是否在公众号白名单
3. 是否为有草稿接口权限的认证服务号
4. token 是否触发频控（每日 2000 次）

错误码全表见 [error-codes.md](error-codes.md)，接口限制见 [wechat-mp-api.md](wechat-mp-api.md)。
