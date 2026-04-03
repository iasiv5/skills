#!/usr/bin/env python3
"""微信公众号草稿箱推送工具

将 format.py 排版后的文章推送到微信公众号草稿箱。
自动上传占位封面图（微信 API 要求 thumb_media_id 有效），发布前由用户在公众号后台替换封面。

用法:
    # 从排版输出目录推送
    python3 publish.py --dir /tmp/wechat-draft/article-name

    # 从 Markdown 一步到位（自动排版再推送）
    python3 publish.py --input article.md --theme newspaper

    # 指定标题/作者
    python3 publish.py --dir /tmp/wechat-draft/article-name --title "标题" --author "作者"

    # 测试模式（不推送草稿箱）
    python3 publish.py --input article.md --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── 路径 ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent


def load_config():
    """加载配置文件"""
    config_path = SKILL_DIR / "config.json"
    if not config_path.exists():
        print("错误: config.json 不存在")
        print(f"  修复: cp {SKILL_DIR / 'config.example.json'} {config_path}")
        print("  然后填写 wechat.app_id 和 wechat.app_secret")
        sys.exit(1)
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"错误: config.json 格式有误 — {e}")
        sys.exit(1)


# ── 微信 API ─────────────────────────────────────────────────────────

ERROR_MESSAGES = {
    -1: "系统繁忙，请稍后重试",
    40001: "access_token 无效或已过期，请检查 APPID/APPSECRET",
    40002: "grant_type 不合法",
    40003: "AppID 不合法",
    40009: "图片大小超过限制（2MB）",
    41001: "缺少 access_token",
    42001: "access_token 已过期",
    43002: "需要 POST 请求",
    45009: "API 调用次数超出限制，请稍后重试",
    45125: "AppSecret 无效，请检查 config.json 中的 app_secret",
    48001: "API 未授权，请在公众号后台开通草稿接口权限",
    40164: "IP 不在白名单中，请到公众号后台 → 设置与开发 → 基本配置 → IP 白名单中添加当前 IP",
    87009: "IP 不在白名单中，请到公众号后台 → 设置与开发 → 基本配置 → IP 白名单中添加当前 IP",
}


def get_access_token(config):
    """获取微信 API access_token，带文件缓存（提前 200s 刷新）"""
    wechat = config.get("wechat", {})
    app_id = wechat.get("app_id", "")
    app_secret = wechat.get("app_secret", "")

    if not app_id or not app_secret or app_id.startswith("YOUR_"):
        print("错误: 请先在 config.json 中配置 wechat.app_id 和 wechat.app_secret")
        sys.exit(1)

    cache_path = Path(wechat.get("token_cache_path", "/tmp/wechat-draft-token.json"))

    # 检查缓存
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if cache.get("expires_at", 0) > time.time() + 200:
                return cache["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass

    # 获取新 token
    print("获取 access_token...")
    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret,
        },
        timeout=15,
    )
    data = resp.json()

    if "access_token" not in data:
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "")
        msg = ERROR_MESSAGES.get(errcode, f"未知错误 (errcode={errcode}): {errmsg}")
        print(f"错误: 获取 access_token 失败 — {msg}")
        sys.exit(1)

    # 缓存
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({
        "access_token": data["access_token"],
        "expires_at": time.time() + data.get("expires_in", 7200) - 200,
    }, ensure_ascii=False))

    print(f"  token 有效期: {data.get('expires_in', '?')} 秒")
    return data["access_token"]


def _compute_file_hash(path, chunk_size=8192):
    """计算文件的 MD5 哈希，用于判断文件是否变化"""
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def upload_cover(token, config):
    """上传封面图并缓存 media_id。优先使用 config.wechat.cover_image 指定的本地图片，
    否则生成 900x383 占位图。同一文件不重复上传（按 MD5 判断）。
    """
    wechat = config.get("wechat", {})
    cover_image = wechat.get("cover_image", "")
    cache_path = Path(wechat.get("cover_cache_path", "/tmp/wechat-draft-cover.json"))

    # 判断图片来源：优先 config 指定 → 内置 assets/cover.jpg → Pillow 占位
    if cover_image and Path(cover_image).exists():
        source_path = Path(cover_image)
        file_hash = _compute_file_hash(source_path)
        source_label = f"自定义封面: {source_path.name}"
    elif (SKILL_DIR / "assets" / "cover.jpg").exists():
        source_path = SKILL_DIR / "assets" / "cover.jpg"
        file_hash = _compute_file_hash(source_path)
        source_label = f"内置封面: assets/cover.jpg"
    else:
        source_path = None
        file_hash = "__placeholder__"
        source_label = "占位封面（Pillow 生成）"

    # 检查缓存：同一文件不重复上传
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if cache.get("file_hash") == file_hash and cache.get("media_id"):
                print(f"  ✓ 使用缓存封面 (media_id: {cache['media_id'][:20]}...)")
                return cache["media_id"]
        except (json.JSONDecodeError, KeyError):
            pass

    # 需要上传
    print(f"  上传{source_label}...")

    try:
        if source_path:
            # 上传本地图片
            ext = source_path.suffix.lower()
            content_type = {
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".gif": "image/gif",
            }.get(ext, "image/jpeg")
            with open(source_path, "rb") as f:
                resp = requests.post(
                    f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
                    files={"media": (source_path.name, f, content_type)},
                    timeout=30,
                )
        else:
            # 生成占位图
            from PIL import Image
            import io as _io
            img = Image.new("RGB", (900, 383), (245, 245, 245))
            buf = _io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            resp = requests.post(
                f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
                files={"media": ("cover.jpg", buf, "image/jpeg")},
                timeout=30,
            )

        data = resp.json()
        if "media_id" in data:
            # 缓存
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps({
                "media_id": data["media_id"],
                "file_hash": file_hash,
            }, ensure_ascii=False))
            return data["media_id"]
        print(f"  警告: 封面上传失败 — {data}")
    except ImportError:
        print("  警告: Pillow 未安装，无法生成占位封面，请在 config.json 中指定 cover_image")
    except Exception as e:
        print(f"  警告: 封面上传异常 — {e}")
    return None


def push_draft(token, title, content, author="", thumb_media_id=""):
    """推送文章到草稿箱"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

    data = {
        "articles": [{
            "title": title,
            "author": author,
            "content": content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }]
    }

    # ensure_ascii=False 防止中文被转义为 \\uXXXX
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    resp = requests.post(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    return resp.json()


# ── 辅助函数 ──────────────────────────────────────────────────────────

def extract_title_from_html(html):
    """从 HTML 中提取 h1 标题"""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return None


def _push_with_cover(config, title, html, author, wechat_config):
    """获取 token → 上传封面 → 推送草稿箱，返回 API 响应"""
    token = get_access_token(config)
    print("✓ token 获取成功")

    print("\n准备封面...")
    thumb_media_id = upload_cover(token, config)
    if not thumb_media_id:
        print("错误: 无法上传占位封面，推送终止")
        sys.exit(1)
    print("✓ 占位封面上传成功")

    print("\n推送到草稿箱...")
    return push_draft(token, title, html, author, thumb_media_id)


def _print_success(media_id, retry=False):
    """打印推送成功信息"""
    label = "推送成功（重试后）!" if retry else "推送成功!"
    print(f"\n{'=' * 40}")
    print(f"  {label}")
    print(f"  草稿 media_id: {media_id}")
    print("  → 请到微信公众号后台 → 草稿箱 查看和发布")
    if not retry:
        print("  → 记得到后台补充封面图后再发布")
    print(f"{'=' * 40}")



# ── 主流程 ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="微信公众号草稿箱推送工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", "-d", help="排版输出目录路径（含 article.html）")
    group.add_argument("--input", "-i", help="Markdown 文件路径（自动排版后推送）")
    parser.add_argument("--title", "-t", default="", help="文章标题（默认从 HTML 提取）")
    parser.add_argument("--theme", default=None, help="排版主题（仅 --input 模式有效）")
    parser.add_argument("--author", "-a", default=None, help="作者名（默认读 config.json）")
    parser.add_argument("--dry-run", action="store_true", help="只排版，不推送草稿箱")
    args = parser.parse_args()

    config = load_config()

    # ── 1. 确定文章目录和 HTML ──────────────────────────────────────
    if args.input:
        # 自动排版模式
        input_path = Path(args.input).resolve()
        if not input_path.exists():
            print(f"错误: 文件不存在 — {input_path}")
            sys.exit(1)

        theme = args.theme or config.get("settings", {}).get("default_theme", "newspaper")
        output_base = Path(config.get("output_dir", "/tmp/wechat-draft"))
        file_stem = re.sub(r"-(公众号|小红书|微博)$", "", input_path.stem)
        article_dir = output_base / file_stem

        print("=== 第一步：排版 ===")
        format_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "format.py"),
            "--input", str(input_path),
            "--theme", theme,
            "--no-open",
        ]
        result = subprocess.run(format_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"排版失败:\n{result.stderr}")
            sys.exit(1)
        if result.stdout:
            print(result.stdout)
    else:
        article_dir = Path(args.dir)

    if not article_dir.exists():
        print(f"错误: 目录不存在 — {article_dir}")
        sys.exit(1)

    # ── 2. 读取 HTML ────────────────────────────────────────────────
    print(f"\n=== {'第二步' if args.input else '第一步'}：准备发布 ===")
    article_path = article_dir / "article.html"

    if not article_path.exists():
        # 兼容：从 preview.html 提取
        preview_path = article_dir / "preview.html"
        if preview_path.exists():
            print("未找到 article.html，从 preview.html 提取...")
            preview_content = preview_path.read_text(encoding="utf-8")
            match = re.search(
                r'<div id="wechatHtml">(.*?)</div>\s*<script>',
                preview_content,
                re.DOTALL,
            )
            if match:
                html = match.group(1).strip()
            else:
                print("错误: 无法从 preview.html 提取文章内容")
                sys.exit(1)
        else:
            print(f"错误: 未找到 article.html 或 preview.html — {article_dir}")
            sys.exit(1)
    else:
        html = article_path.read_text(encoding="utf-8")

    # ── 3. 提取标题和作者 ────────────────────────────────────────────
    title = args.title or extract_title_from_html(html) or article_dir.name
    wechat_config = config.get("wechat", {})
    author = args.author or wechat_config.get("author", "") or config.get("settings", {}).get("default_author", "")
    print(f"标题: {title}")
    print(f"作者: {author or '(空)'}")

    # ── 4. dry-run 模式 ──────────────────────────────────────────────
    if args.dry_run:
        print(f"\n[dry-run] 跳过推送草稿箱")
        print(f"  标题: {title}")
        print(f"  作者: {author}")
        print(f"  HTML 长度: {len(html)} 字符")
        return

    # ── 5. 获取 token → 上传封面 → 推送草稿箱 ────────────────────────
    result = _push_with_cover(config, title, html, author, wechat_config)

    if "media_id" in result:
        _print_success(result["media_id"])
    else:
        errcode = result.get("errcode", "?")
        errmsg = result.get("errmsg", "未知错误")
        msg = ERROR_MESSAGES.get(errcode, f"未知错误 (errcode={errcode}): {errmsg}")
        print(f"\n推送失败 — {msg}")

        # token 过期：清缓存重试一次
        if errcode in (40001, 42001):
            print("  重试: 清除 token 缓存，重新获取...")
            cache_path = Path(wechat_config.get("token_cache_path", "/tmp/wechat-draft-token.json"))
            if cache_path.exists():
                cache_path.unlink()
            result = _push_with_cover(config, title, html, author, wechat_config)
            if "media_id" in result:
                _print_success(result["media_id"], retry=True)
            else:
                errcode2 = result.get("errcode", "?")
                errmsg2 = result.get("errmsg", "")
                print(f"  重试仍然失败 (errcode={errcode2}: {errmsg2})")
                sys.exit(1)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
