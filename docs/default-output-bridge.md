# 默认输出 bridge（第一阶段）

## 目标

把“值得归档的长输出”在最终回复前，稳定转成一份 `PublishRequest`，交给 `publish_to_newspaper.py`，然后把**摘要 + 链接**回到聊天。

第一阶段不追求：
- 取代聊天窗口
- 实时双向会话 UI
- 把所有消息都落报纸
- 复杂队列、权限、多租户

## 最小触发点

最短接入点不在前端，而在：

1. 主代理或项目代理完成一篇高质量长输出
2. finalize 阶段做一次判定：是否属于应归档内容
3. 命中则构造 `PublishRequest`
4. 调用 `publish_to_newspaper.py`
5. 聊天里只返回摘要 + edition/project 链接

## 哪些内容应触发

建议第一阶段只收：
- 调研报告
- 项目阶段总结
- rollout / 实施计划
- 高质量长回答

不收：
- 简短问答
- 过程性碎片
- yes/no
- 闲聊

## 最小输入 contract

```json
{
  "project": { "slug": "OpenClaw-Newspaper-UI" },
  "edition": {
    "title": "本轮系统推进摘要",
    "summary": "把报纸系统推进到第一阶段可用。",
    "density": "longform",
    "tags": ["status", "publish"]
  },
  "content": {
    "bodyHtml": "<h2>结论</h2><p>……</p>"
  },
  "source": {
    "sessionId": "public-demo",
    "channel": "feishu"
  },
  "options": {
    "updateProjectMeta": false,
    "rebuildPortal": true,
    "rebuildProjectPage": true
  }
}
```

## 调用方式

```bash
python scripts/publish_bridge_example.py --input examples/default-output-sample.json --dry-run
python scripts/publish_bridge_example.py --input examples/default-output-sample.json --publish
```

bridge 示例脚本会：
- 读取较松散的“默认输出输入对象”
- 归一化成 `PublishRequest`
- dry-run 时只打印 request
- publish 时落到 `data/requests/` 并调用 `publish_to_newspaper.py`

## 第一阶段边界

- source-of-truth 是 `data/source/*.json`
- `site/data/portal-index.json` 是编译结果，不是手工真源
- bridge 只负责把输出送进发布入口，不直接改页面
- 真正的主会话 hook / relay 仍是后续阶段能力
