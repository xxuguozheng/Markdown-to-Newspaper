# 项目接口层（最小可用）

更新时间：2026-03-08

本轮补齐两个最小 CLI / JSON request 接口：

- `create_project`
- `update_project_meta`

目标不是做完整后台，而是给现有 source-of-truth + render pipeline 增加一个稳定可复用的最小项目管理入口。

## 脚本

```bash
python scripts/project_interface.py --action create_project --request <json>
python scripts/project_interface.py --action update_project_meta --request <json>
```

可选参数：

```bash
--dry-run
```

dry-run 会做校验并返回 receipt，但不会写入 `data/source/projects.json`，也不会触发 render。

## create_project 请求格式

必填字段：

- `slug`
- `label`
- `description`
- `summary`
- `stage`
- `blockers`
- `next`
- `status`

示例：

```json
{
  "slug": "TEST-Project-Interface-2026-03-08",
  "label": "TEST Project Interface 2026-03-08",
  "description": "用于验证 create_project / update_project_meta 的最小测试项目。",
  "summary": "这是一个明显测试名项目，用来验证最小项目接口层、渲染链和门户刷新。",
  "stage": "接口验证中",
  "blockers": "暂无真实业务阻塞；仅用于接口验证。",
  "next": "先完成 create_project，再执行 update_project_meta。",
  "status": "active"
}
```

行为：

1. 校验请求字段是否齐全
2. 校验 `slug` 唯一性
3. 生成 `project.id`
4. 写入 `data/source/projects.json`
5. 创建 `projects/<slug>/`
6. 调用 `scripts/render_newspaper.py` 触发重渲染
7. 返回 receipt，并写入 `data/receipts/`

## update_project_meta 请求格式

必填：

- `slug`

可更新字段：

- `label`
- `description`
- `summary`
- `stage`
- `blockers`
- `next`
- `status`

示例：

```json
{
  "slug": "TEST-Project-Interface-2026-03-08",
  "summary": "测试项目已完成 update_project_meta 验证，说明最小元数据更新链路可用。",
  "stage": "接口验证完成",
  "blockers": "暂无；当前剩余工作主要是把 CLI/JSON 接口接进更高层运行时。",
  "next": "如需产品化，可继续补真正的后台入口或主运行时调用面。",
  "status": "active"
}
```

行为：

1. 用 `slug` 找到目标项目
2. 仅覆盖 request 中显式提供的字段
3. 刷新 `updatedAt`
4. 写回 `data/source/projects.json`
5. 触发 render
6. 返回 receipt，并写入 `data/receipts/`

## receipt 结构（当前最小版）

返回字段包括：

- `ok`
- `action`
- `projectId`
- `projectSlug`
- `projectUrl`
- `portalUrl`
- `changedFields`
- `projectCreated`
- `rendered`
- `dryRun`
- `updatedAt`
- `requestPath`
- `receiptPath`（非 dry-run）

## 验证记录

本轮已真实执行：

1. `create_project --dry-run`
2. `create_project` 真创建
3. `update_project_meta` 真更新
4. `python scripts/render_newspaper.py` 重渲染

验证用项目：

- `TEST-Project-Interface-2026-03-08`

它被故意保留在项目列表里，作为接口验证痕迹，避免把真实项目数据混淆成无来源的手工改动。

## 这轮没做的

- 没做 Web / UI 后台
- 没做权限系统
- 没做并发写保护 / 文件锁
- 没把项目接口接进主运行时 finalize hook
- 没扩展 edition 创建之外的复杂项目生命周期操作
