# Runtime integration note: 默认重要长输出 → OpenClaw Newspaper

更新时间：2026-03-08

## 这份 note 解决什么

把当前已经可用的 publish pipeline，往“主运行时准默认接入”再推进半步：

- 明确 **最小接线点** 在 reply finalize 之后、真正发回聊天之前
- 明确 **分流规则**：哪些输出默认进报纸，哪些不进
- 提供一层 **不改 OpenClaw 主源码也能先跑的 helper**
- 固化一份 **runtime-facing contract**，让后续接主运行时时不需要再重新想一次

当前结论很简单：

> 现在不缺 publish pipeline，本轮最缺的是 **finalize 结果对象 → publish decision → chat reply contract** 这一截。

---

## 当前已具备的东西

项目里已经有：

1. `scripts/publish_to_newspaper.py`
   - 接收 `PublishRequest`
   - 产出版次 HTML
   - 写入 `data/source/editions.json`
   - 重渲染项目页和门户
   - 写 receipt

2. `scripts/publish_bridge_example.py`
   - 能把较松散的输入转成 `PublishRequest`
   - 适合做概念验证
   - 但它还是 demo bridge，不是 runtime helper

3. `docs/default-output-bridge.md`
   - 已明确最短接入点在 finalize 阶段
   - 已说明只让高价值长输出进报纸

所以现在真正差的不是“能不能发布”，而是：

- 主代理最后一跳的输出对象长什么样
- 判定规则谁来执行
- 命中后聊天里回什么
- 未命中时如何保持普通回复直出

---

## 从 publish bridge 到主代理回复流程，还差的最小接线点

最小只差 4 个点：

### 1. finalize payload 要有稳定输入面

建议主代理 finalize 之后先形成一个内部对象，至少包含：

```json
{
  "project": { "slug": "OpenClaw-Newspaper-UI" },
  "output": {
    "kind": "plan",
    "title": "重要长输出自动进报纸的最小接线方案",
    "summary": "……",
    "density": "longform",
    "tags": ["runtime", "plan"],
    "text": "……",
    "bodyHtml": "<article>……</article>"
  },
  "source": {
    "sessionId": "public-demo",
    "channel": "feishu",
    "role": "main-agent"
  },
  "options": {
    "updateProjectMeta": false,
    "rebuildPortal": true,
    "rebuildProjectPage": true
  },
  "routing": {
    "forcePublish": false,
    "skipPublish": false
  }
}
```

关键不是字段多，而是把 **“这是一篇什么类型的最终输出”** 明确表达出来。

### 2. finalize 后要有一个 publish decision

这个 decision 不该散落在 prompt 文案里，也不该靠“感觉像长文”。

应该有一个明确 helper：

- 输入：finalize payload
- 输出：
  - `shouldPublish`
  - `reasons`
  - `normalizedRequest`
  - `receipt`（如果真的发布了）
  - `chatReply`

### 3. 聊天回复需要两种模式

命中报纸分流时：
- 聊天里不再原样贴整篇长文
- 只回：摘要 + edition/project 链接

未命中时：
- 维持普通聊天直出

也就是说，主运行时最终要支持：

- `mode = summary-plus-links`
- `mode = direct-chat`

### 4. 主运行时只需要接 helper，不需要理解报纸内部细节

主运行时完全没必要知道：
- source-of-truth 如何存
- 版次 id 怎么生成
- 页面怎么渲染
- receipt 怎么写

它只需要在 finalize 后调用 helper，吃回一个结果对象。

这就是最小接线。

---

## 本轮新增的更实用 helper

已新增：

- `scripts/default_output_runtime_helper.py`
- `examples/default-output-runtime-input.json`

### helper 职责

这个脚本不是 demo bridge，而是更接近 runtime 对接面：

1. 读一份 finalize payload
2. 根据规则判断 `shouldPublish`
3. 归一化成 `PublishRequest`
4. 如需发布，则落 request 并调用 `publish_to_newspaper.py`
5. 返回一个主运行时可直接消费的结果对象

### 命令

只做判定：

```bash
python scripts/default_output_runtime_helper.py \
  --input examples/default-output-runtime-input.json \
  --decide-only
```

判定并发布：

```bash
python scripts/default_output_runtime_helper.py \
  --input examples/default-output-runtime-input.json \
  --publish
```

---

## helper 输出 contract（建议主运行时直接对齐）

```json
{
  "ok": true,
  "shouldPublish": true,
  "reasons": [
    "kind=plan is publish-worthy",
    "density=longform is archive-worthy",
    "html/bodyHtml available"
  ],
  "normalizedRequest": { "...": "..." },
  "receipt": {
    "editionUrl": "/projects/OpenClaw-Newspaper-UI/...html",
    "projectUrl": "/projects/OpenClaw-Newspaper-UI/index.html",
    "portalUrl": "/site/index.html"
  },
  "chatReply": {
    "mode": "summary-plus-links",
    "summary": "……",
    "editionUrl": "…",
    "projectUrl": "…",
    "portalUrl": "…",
    "suggestedText": "摘要\n\n报纸版：…\n项目页：…"
  }
}
```

未命中时：

```json
{
  "ok": true,
  "shouldPublish": false,
  "reasons": ["kind=chat is configured to skip"],
  "normalizedRequest": { "...": "..." },
  "receipt": null,
  "chatReply": {
    "mode": "direct-chat",
    "summary": "……",
    "suggestedText": "完整聊天回复正文"
  }
}
```

---

## 明确分流规则：哪些默认进报纸，哪些不进

这一条必须写死到实现 note，不然“准默认输出”会永远停在口头。

### 默认进报纸

满足任一核心条件即可进入候选：

#### A. 输出类型命中

`output.kind` 属于：

- `report`
- `plan`
- `status-update`
- `research`
- `briefing`
- `long-answer`

#### B. 密度命中

`output.density` 属于：

- `longform`
- `frontpage`

#### C. 结构命中

满足任一：

- 提供 `bodyHtml` / `html`
- `text` 很长（当前 helper 用 `>= 1200 chars` 作为极粗门槛）
- `summary` 本身已像一个可归档摘要

### 默认不进报纸

`output.kind` 属于以下直接跳过：

- `chat`
- `small-talk`
- `yes-no`
- `tool-log`
- `process-update`
- `short-answer`

### 显式覆盖

为了给主代理留判断余地：

- `routing.forcePublish = true` → 强制进报纸
- `routing.skipPublish = true` → 强制不进报纸

这比把规则完全写死在提示词里稳得多。

---

## 推荐的主运行时接线顺序

### Phase A：现在就能做（不改主源码的外部接桥）

由管理层或包装层在真正回消息前：

1. 先产出 finalize payload JSON
2. 调 `default_output_runtime_helper.py`
3. 读结果：
   - `shouldPublish=true` → 用 `chatReply.suggestedText`
   - `shouldPublish=false` → 用 `chatReply.suggestedText` 直回

这一步已经足够把“重要长输出自动进报纸”跑成外部包装层能力。

### Phase B：主运行时内建接桥

等需要真正默认化时，把 helper 逻辑内收到宿主 finalize path：

1. finalize 产生统一对象
2. 内部路由器执行 publish decision
3. 命中则走 publish pipeline
4. 渠道层发送摘要 + 链接
5. 同时保留普通直出路径

### Phase C：再往后才考虑的事

不是当前最小接线必须项：

- 草稿预览 / 审核 UI
- 失败重试队列
- 并发锁 / 去重键
- 同一会话多版本覆盖策略
- 更精细的项目自动归档策略

---

## 为什么说“离准默认报纸输出还差哪一步”只差一步

因为真正没接上的，只是：

> **把主代理 finalize 的最终内容对象，稳定送进 helper。**

更具体地说，离“准默认报纸输出”还差这一个宿主侧动作：

- 在主代理/项目代理的最终回复路径里，增加一次 **finalize payload 组装 + helper 调用**

不是还差整套系统，不是还差前端，不是还差数据库。

publish pipeline 已有，项目页/门户也会重渲染，聊天返回 contract 现在也有了。

剩下就是把这次 helper 真正挂到主回复链路上。

---

## 最小伪代码

```python
final_payload = build_finalize_payload(answer)
result = run_runtime_helper(final_payload)

if result["shouldPublish"]:
    send_chat(result["chatReply"]["suggestedText"])
else:
    send_chat(result["chatReply"]["suggestedText"])
```

注意：
- 两条路径最后都是 `send_chat(...)`
- 区别只在于发送内容不同
- 报纸系统不应该侵入渠道层太深

---

## 当前 helper 的边界

已足够实用，但还不是最终形态：

1. 规则仍是启发式，不是宿主级统一策略
2. 没有去重键
3. 没有失败回退策略（例如 publish 失败时自动退回完整直出）
4. slug 仍继承现有 `publish_to_newspaper.py` 的策略
5. 项目自动归档仍主要靠上游显式给 `project.slug`

这些都属于下一层优化，不阻塞当前“准默认化接桥”。

---

## 建议的下一步实施顺序

1. **先把主代理 finalize payload 固定下来**
   - 至少固定：`kind/title/summary/density/text/bodyHtml/source`

2. **在外部包装层实际调用 helper 一次**
   - 先不要动核心主源码
   - 让真实一条长输出走通“自动进报纸”

3. **补一个 publish 失败回退**
   - 如果 helper 发布失败，自动降级成 direct-chat

4. **再考虑主运行时内建化**
   - 这时只是把 helper 逻辑内收，不再是重新设计

---

## 一句话结论

当前项目已经不是“缺报纸发布能力”，而是只差把 **finalize 结果 → runtime helper** 这一步真接上。

接上之后，就已经能算 **准默认报纸输出**：

- 重要长输出默认进报纸
- 聊天里只回摘要和链接
- 普通短回复继续走原聊天路径
