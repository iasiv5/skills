# 微信公众号 MP API 参考

## 获取 Access Token

```
GET https://api.weixin.qq.com/cgi-bin/token
    ?grant_type=client_credential
    &appid=APPID
    &secret=APPSECRET
```

响应：
```json
{"access_token": "TOKEN", "expires_in": 7200}
```

错误：
```json
{"errcode": 40001, "errmsg": "invalid credential"}
```

## 创建草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=TOKEN
Content-Type: application/json
```

请求体：
```json
{
  "articles": [{
    "title": "文章标题",
    "author": "作者",
    "digest": "摘要（可选，不填则不显示摘要）",
    "content": "<p>HTML 内容</p>",
    "content_source_url": "原文链接（可选）",
    "thumb_media_id": "封面图 media_id（可为空字符串）",
    "need_open_comment": 0,
    "only_fans_can_comment": 0
  }]
}
```

响应：
```json
{"media_id": "DRAFT_MEDIA_ID"}
```

注意：
- 请求体必须 `ensure_ascii=False` + UTF-8 编码
- `thumb_media_id` 传空字符串可创建无封面草稿
- 发布前需在公众号后台补充封面图

## 获取草稿列表

```
POST https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=TOKEN
```

请求体：
```json
{"offset": 0, "count": 20, "no_content": 1}
```

## 删除草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/delete?access_token=TOKEN
```

请求体：
```json
{"media_id": "DRAFT_MEDIA_ID"}
```

## 上传永久图片素材（封面用）

```
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=TOKEN&type=image
Content-Type: multipart/form-data
```

Body: `media=<file>`

响应：
```json
{"media_id": "MEDIA_ID", "url": "http://..."}
```

限制：图片最大 2MB，支持 jpg/png/gif。

## 上传正文图片

```
POST https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=TOKEN
Content-Type: multipart/form-data
```

Body: `media=<file>`

响应：
```json
{"url": "https://mmbiz.qpic.cn/..."}
```

返回的 URL 可直接用于 `<img src="...">`。
