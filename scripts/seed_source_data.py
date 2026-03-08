#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from newspaper_data import dump_json, ensure_dirs, slugify

ROOT = Path(__file__).resolve().parent.parent
PORTAL_INDEX = ROOT / 'site' / 'data' / 'portal-index.json'
PROJECTS_OUT = ROOT / 'data' / 'source' / 'projects.json'
EDITIONS_OUT = ROOT / 'data' / 'source' / 'editions.json'


def project_id_from_slug(slug: str) -> str:
    return slug.lower().replace('_', '-').replace(' ', '-').replace('--', '-')


def make_edition_id(project_id: str, date_hint: str, idx: int) -> str:
    compact = date_hint[:10].replace('-', '') if date_hint else 'unknown'
    return f'edition_{project_id.replace('-', '_')}_{compact}_{idx:03d}'


def main() -> None:
    ensure_dirs()
    portal = json.loads(PORTAL_INDEX.read_text(encoding='utf-8'))
    generated_at = portal.get('generatedAt') or datetime.now().astimezone().isoformat(timespec='seconds')
    projects = []
    editions = []
    for slug, payload in portal.get('projects', {}).items():
        info = payload.get('info', {})
        items = payload.get('items', [])
        project_id = project_id_from_slug(slug)
        latest_updated = info.get('updated') or (items[0].get('updatedAt') if items else generated_at)
        projects.append({
            'id': project_id,
            'slug': slug,
            'label': payload.get('label', slug),
            'description': payload.get('description', ''),
            'summary': info.get('summary', payload.get('description', '')),
            'stage': info.get('stage', '待补充'),
            'blockers': info.get('blockers', ''),
            'next': info.get('next', ''),
            'updatedAt': latest_updated,
            'status': 'active',
        })
        for idx, item in enumerate(items, start=1):
            published_at = item.get('updatedAt') or latest_updated
            editions.append({
                'id': make_edition_id(project_id, str(published_at), idx),
                'projectId': project_id,
                'projectSlug': slug,
                'slug': item.get('rawTitle') or slugify(item.get('title', 'edition')),
                'title': item.get('title', item.get('rawTitle', 'Untitled')),
                'rawTitle': item.get('rawTitle', slugify(item.get('title', 'edition'))),
                'summary': item.get('summary', ''),
                'density': item.get('density', 'brief'),
                'densityLabel': item.get('densityLabel', '快报 / 小更新'),
                'htmlUrl': item.get('url'),
                'publishedAt': published_at,
                'updatedAt': published_at,
                'size': item.get('size', 0),
                'tags': [],
                'source': {'type': 'manual', 'sessionId': 'unknown', 'channel': 'unknown'},
            })
    dump_json(PROJECTS_OUT, {'generatedAt': generated_at, 'projects': projects})
    dump_json(EDITIONS_OUT, {'generatedAt': generated_at, 'editions': editions})
    print(f'seeded {len(projects)} projects and {len(editions)} editions')


if __name__ == '__main__':
    main()
