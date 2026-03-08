# OpenClaw Newspaper Archive

这个目录用于归档 Staro 生成的报纸式网页输出。

## 当前阶段：第一阶段可用系统

本轮已把项目从“静态 HTML + 手工维护索引”推进到**最小可发布系统**：

- `data/source/projects.json`：项目真源
- `data/source/editions.json`：版次真源
- `scripts/newspaper_data.py`：数据读写与 schema 校验辅助
- `scripts/seed_source_data.py`：从当前 `site/data/portal-index.json` 迁移/回填真源
- `scripts/render_newspaper.py`：从真源渲染项目页、门户页和 `site/data/portal-index.json`
- `scripts/publish_to_newspaper.py`：最小发布流水线，负责写入版次、更新真源、重渲染页面
- `scripts/project_interface.py`：最小项目接口层，负责 `create_project` / `update_project_meta`
- `scripts/publish_bridge_example.py`：默认输出接入示例，把一次长输出包装成 `PublishRequest`
- `scripts/default_output_runtime_helper.py`：更接近主运行时的 helper，负责判定是否应进报纸、归一化 request，并返回聊天回复 contract
- `docs/runtime-integration-note.md`：从 publish bridge 到主代理 finalize 接线的具体实施 note
- `docs/project-interface.md`：项目接口层使用说明与验证记录

## 目录约定

- `data/source/`：唯一 source-of-truth 数据层
- `data/receipts/`：发布回执
- `data/requests/`：示例或待提交发布请求
- `projects/[项目名]/`：按项目归档的报纸页与聚合页
- `site/`：门户页及其编译结果
- `templates/`：门户页与项目页模板

## 最小 schema

### Project

字段：
- `id`
- `slug`
- `label`
- `description`
- `summary`
- `stage`
- `blockers`
- `next`
- `updatedAt`
- `status`

### Edition

字段：
- `id`
- `projectId`
- `projectSlug`
- `slug`
- `title`
- `rawTitle`
- `summary`
- `density`
- `densityLabel`
- `htmlUrl`
- `publishedAt`
- `updatedAt`
- `size`
- `tags`
- `source`

### PublishRequest

字段：
- `project.slug`
- `edition.title`
- `edition.summary`
- `edition.density`
- `edition.tags`
- `content.html` 或 `content.bodyHtml`
- `source.sessionId`
- `source.channel`
- `options.rebuildPortal`
- `options.rebuildProjectPage`

### PublishReceipt

字段：
- `ok`
- `projectId`
- `projectSlug`
- `editionId`
- `editionUrl`
- `projectUrl`
- `portalUrl`
- `rebuilt`
- `publishedAt`
- `requestPath`

## 默认规则

- 长回复 / 复杂问题 / 方案说明优先存为报纸页
- 默认按项目归档
- `site/data/portal-index.json` 视为渲染产物，不再是主真源

## 常用命令

```bash
cd .

# 1. 从旧 portal-index 回填真源
python scripts/seed_source_data.py

# 2. 用真源重渲染门户与项目页
python scripts/render_newspaper.py

# 3. 发布一篇新报纸
python scripts/publish_to_newspaper.py --request data/requests/example-publish-request.json

# 4. 新建项目（dry-run）
python scripts/project_interface.py --action create_project --request examples/create-project-test-2026-03-08.json --dry-run

# 5. 新建项目（真实写入）
python scripts/project_interface.py --action create_project --request examples/create-project-test-2026-03-08.json

# 6. 更新项目元信息
python scripts/project_interface.py --action update_project_meta --request examples/update-project-meta-test-2026-03-08.json

# 7. 演示默认输出 bridge（dry-run）
python scripts/publish_bridge_example.py --input examples/default-output-sample.json --dry-run

# 8. 演示更接近 runtime 的 helper（只做判定）
python scripts/default_output_runtime_helper.py --input examples/default-output-runtime-input.json --decide-only

# 9. 演示更接近 runtime 的 helper（直接发布）
python scripts/default_output_runtime_helper.py --input examples/default-output-runtime-input.json --publish
```
