#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from newspaper_data import (
    ROOT,
    RECEIPTS_DIR,
    dump_json,
    ensure_dirs,
    find_project,
    load_editions,
    load_projects,
    save_editions,
    slugify,
    validate_edition,
    validate_project,
    validate_publish_receipt,
    validate_publish_request,
)
from render_newspaper import run_render


def next_edition_id(project_id: str, published_at: str, current_count: int) -> str:
    compact = published_at[:10].replace('-', '')
    return f"edition_{project_id.replace('-', '_')}_{compact}_{current_count + 1:03d}"


def density_label(density: str) -> str:
    return {
        'brief': '快报 / 小更新',
        'longform': '长分析 / 方案稿',
        'frontpage': '头版 / 项目总况',
    }.get(density, '快报 / 小更新')


def render_html_document(title: str, summary: str, body_html: str, published_at: str) -> str:
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body{{margin:0;background:#ddd6c8;color:#171717;font-family:"Source Han Serif SC","Songti SC",serif;}}
    .page{{max-width:1100px;margin:24px auto;background:#f5f1e8;padding:24px 28px;box-shadow:0 12px 36px rgba(0,0,0,.18);}}
    .topline{{font:11px/1.4 Inter,sans-serif;color:#666;text-transform:uppercase;letter-spacing:.08em;}}
    h1{{margin:8px 0 10px;font-size:clamp(32px,4vw,58px);line-height:.95;}} .summary{{font:16px/1.65 Inter,sans-serif;margin-bottom:18px;color:#2b251f;}}
    .body{{font-size:17px;line-height:1.72;}} .body h2{{margin-top:28px;}} .body p{{margin:0 0 14px;}}
  </style>
</head>
<body>
  <main class="page">
    <div class="topline">OpenClaw Newspaper · {published_at}</div>
    <h1>{title}</h1>
    <div class="summary">{summary}</div>
    <article class="body">{body_html}</article>
  </main>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Publish one edition to OpenClaw Newspaper')
    parser.add_argument('--request', required=True, help='Path to PublishRequest JSON')
    args = parser.parse_args()

    ensure_dirs()
    request_path = Path(args.request)
    request = json.loads(request_path.read_text(encoding='utf-8'))
    validate_publish_request(request)

    projects = load_projects()
    editions = load_editions()
    project = find_project(projects, request['project']['slug'])
    if not project:
        raise SystemExit(f"Unknown project slug: {request['project']['slug']}")
    validate_project(project)

    published_at = request['edition'].get('publishedAt') or datetime.now().astimezone().isoformat(timespec='seconds')
    slug = request['edition'].get('slug') or slugify(request['edition']['title'])
    body_html = request['content'].get('bodyHtml') or request['content'].get('html')
    html = request['content'].get('html') if request['content'].get('html', '').lstrip().startswith('<!doctype html') else render_html_document(request['edition']['title'], request['edition'].get('summary', ''), body_html, published_at)

    project_editions = [e for e in editions if e['projectSlug'] == project['slug']]
    edition_id = next_edition_id(project['id'], published_at, len(project_editions))
    html_rel = f"/projects/{project['slug']}/{slug}.html"
    html_path = ROOT / html_rel.lstrip('/')
    html_path.write_text(html, encoding='utf-8')

    edition = {
        'id': edition_id,
        'projectId': project['id'],
        'projectSlug': project['slug'],
        'slug': slug,
        'title': request['edition']['title'],
        'rawTitle': slug,
        'summary': request['edition'].get('summary', ''),
        'density': request['edition'].get('density', 'brief'),
        'densityLabel': density_label(request['edition'].get('density', 'brief')),
        'htmlUrl': html_rel,
        'publishedAt': published_at,
        'updatedAt': published_at,
        'size': html_path.stat().st_size,
        'tags': request['edition'].get('tags', []),
        'source': request.get('source', {}),
    }
    validate_edition(edition)
    editions.insert(0, edition)
    save_editions(editions)

    project['updatedAt'] = published_at
    if request['options'].get('updateProjectMeta'):
        project['summary'] = request['project'].get('summary', project['summary'])
    from newspaper_data import save_projects
    save_projects(projects)

    run_render(ROOT / 'data' / 'source' / 'projects.json', ROOT / 'data' / 'source' / 'editions.json')

    receipt = {
        'ok': True,
        'projectId': project['id'],
        'projectSlug': project['slug'],
        'editionId': edition_id,
        'editionUrl': html_rel,
        'projectUrl': f"/projects/{project['slug']}/index.html",
        'portalUrl': '/site/index.html',
        'rebuilt': ['edition', 'project', 'portal'],
        'publishedAt': published_at,
        'requestPath': str(request_path),
    }
    validate_publish_receipt(receipt)
    receipt_path = RECEIPTS_DIR / f'{edition_id}.json'
    dump_json(receipt_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
