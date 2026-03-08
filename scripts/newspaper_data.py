#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
SOURCE_DIR = DATA_DIR / 'source'
REQUESTS_DIR = DATA_DIR / 'requests'
RECEIPTS_DIR = DATA_DIR / 'receipts'
PROJECTS_PATH = SOURCE_DIR / 'projects.json'
EDITIONS_PATH = SOURCE_DIR / 'editions.json'

PROJECT_REQUIRED = [
    'id', 'slug', 'label', 'description', 'summary',
    'stage', 'blockers', 'next', 'updatedAt', 'status'
]
EDITION_REQUIRED = [
    'id', 'projectId', 'projectSlug', 'slug', 'title', 'rawTitle', 'summary',
    'density', 'densityLabel', 'htmlUrl', 'publishedAt', 'updatedAt',
    'size', 'tags', 'source'
]
PUBLISH_REQUEST_REQUIRED = ['project', 'edition', 'content', 'source', 'options']
PUBLISH_RECEIPT_REQUIRED = ['ok', 'projectId', 'projectSlug', 'editionId', 'editionUrl', 'projectUrl', 'portalUrl', 'rebuilt', 'publishedAt']


def ensure_dirs() -> None:
    for p in [SOURCE_DIR, REQUESTS_DIR, RECEIPTS_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_projects() -> list[dict[str, Any]]:
    data = load_json(PROJECTS_PATH, {'projects': []})
    return data.get('projects', [])


def load_editions() -> list[dict[str, Any]]:
    data = load_json(EDITIONS_PATH, {'editions': []})
    return data.get('editions', [])


def save_projects(projects: list[dict[str, Any]]) -> None:
    current = load_json(PROJECTS_PATH, {}) or {}
    dump_json(PROJECTS_PATH, {'generatedAt': current.get('generatedAt'), 'projects': projects})


def save_editions(editions: list[dict[str, Any]]) -> None:
    current = load_json(EDITIONS_PATH, {}) or {}
    dump_json(EDITIONS_PATH, {'generatedAt': current.get('generatedAt'), 'editions': editions})


def _validate_required(item: dict[str, Any], required: list[str], kind: str) -> None:
    missing = [k for k in required if k not in item]
    if missing:
        raise ValueError(f'{kind} missing required keys: {missing}')


def validate_project(project: dict[str, Any]) -> None:
    _validate_required(project, PROJECT_REQUIRED, 'Project')


def validate_edition(edition: dict[str, Any]) -> None:
    _validate_required(edition, EDITION_REQUIRED, 'Edition')


def validate_publish_request(request: dict[str, Any]) -> None:
    _validate_required(request, PUBLISH_REQUEST_REQUIRED, 'PublishRequest')
    if 'slug' not in request['project']:
        raise ValueError('PublishRequest.project.slug is required')
    if 'title' not in request['edition']:
        raise ValueError('PublishRequest.edition.title is required')
    if not request['content'].get('html') and not request['content'].get('bodyHtml'):
        raise ValueError('PublishRequest.content.html or content.bodyHtml is required')


def validate_publish_receipt(receipt: dict[str, Any]) -> None:
    _validate_required(receipt, PUBLISH_RECEIPT_REQUIRED, 'PublishReceipt')


def slugify(text: str) -> str:
    raw = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text.strip())
    while '--' in raw:
        raw = raw.replace('--', '-')
    return raw.strip('-') or 'edition'


def find_project(projects: list[dict[str, Any]], slug: str) -> dict[str, Any] | None:
    for p in projects:
        if p['slug'] == slug:
            return p
    return None
