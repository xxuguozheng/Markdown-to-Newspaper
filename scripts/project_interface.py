#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from newspaper_data import (
    ROOT,
    dump_json,
    ensure_dirs,
    find_project,
    load_projects,
    save_projects,
    slugify,
    validate_project,
)
from render_newspaper import run_render

REQUEST_FIELDS = ['slug', 'label', 'description', 'summary', 'stage', 'blockers', 'next', 'status']
MUTABLE_FIELDS = ['label', 'description', 'summary', 'stage', 'blockers', 'next', 'status']
DEFAULT_STATUS = 'active'

DATA_DIR = ROOT / 'data'
REQUESTS_DIR = DATA_DIR / 'requests'
RECEIPTS_DIR = DATA_DIR / 'receipts'
PROJECTS_PATH = ROOT / 'data' / 'source' / 'projects.json'
EDITIONS_PATH = ROOT / 'data' / 'source' / 'editions.json'


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def project_id_from_slug(slug: str) -> str:
    return slugify(slug)


def validate_create_request(request: dict[str, Any]) -> None:
    missing = [field for field in REQUEST_FIELDS if field not in request]
    if missing:
        raise ValueError(f'create_project missing required fields: {missing}')
    if not str(request.get('slug', '')).strip():
        raise ValueError('create_project.slug must be non-empty')


def validate_update_request(request: dict[str, Any]) -> None:
    if not str(request.get('slug', '')).strip():
        raise ValueError('update_project_meta.slug must be non-empty')
    provided = [field for field in MUTABLE_FIELDS if field in request]
    if not provided:
        raise ValueError(f'update_project_meta requires at least one updatable field: {MUTABLE_FIELDS}')


def normalize_text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()


def build_project_from_request(request: dict[str, Any], updated_at: str) -> dict[str, Any]:
    slug = normalize_text(request['slug'])
    project = {
        'id': project_id_from_slug(slug),
        'slug': slug,
        'label': normalize_text(request['label']),
        'description': normalize_text(request['description']),
        'summary': normalize_text(request['summary']),
        'stage': normalize_text(request['stage']),
        'blockers': normalize_text(request['blockers']),
        'next': normalize_text(request['next']),
        'updatedAt': updated_at,
        'status': normalize_text(request.get('status', DEFAULT_STATUS)) or DEFAULT_STATUS,
    }
    validate_project(project)
    return project


def build_receipt(*, action: str, project: dict[str, Any], changed_fields: list[str], request_path: str, dry_run: bool, rendered: bool, project_created: bool) -> dict[str, Any]:
    return {
        'ok': True,
        'action': action,
        'projectId': project['id'],
        'projectSlug': project['slug'],
        'projectUrl': f"/projects/{project['slug']}/index.html",
        'portalUrl': '/site/index.html',
        'changedFields': changed_fields,
        'projectCreated': project_created,
        'rendered': rendered,
        'dryRun': dry_run,
        'updatedAt': project['updatedAt'],
        'requestPath': request_path,
    }


def create_project(request: dict[str, Any], request_path: Path, dry_run: bool) -> dict[str, Any]:
    validate_create_request(request)
    projects = load_projects()
    slug = normalize_text(request['slug'])
    if find_project(projects, slug):
        raise ValueError(f'Project slug already exists: {slug}')

    updated_at = request.get('updatedAt') or now_iso()
    project = build_project_from_request(request, updated_at)
    project_dir = ROOT / 'projects' / project['slug']

    if dry_run:
        return build_receipt(
            action='create_project',
            project=project,
            changed_fields=REQUEST_FIELDS,
            request_path=str(request_path),
            dry_run=True,
            rendered=False,
            project_created=True,
        )

    projects.append(project)
    save_projects(projects)
    project_dir.mkdir(parents=True, exist_ok=True)
    run_render(PROJECTS_PATH, EDITIONS_PATH)
    receipt = build_receipt(
        action='create_project',
        project=project,
        changed_fields=REQUEST_FIELDS,
        request_path=str(request_path),
        dry_run=False,
        rendered=True,
        project_created=True,
    )
    receipt_path = RECEIPTS_DIR / f"project-create-{project['id']}-{updated_at[:19].replace(':', '-')}.json"
    dump_json(receipt_path, receipt)
    receipt['receiptPath'] = str(receipt_path)
    return receipt


def update_project_meta(request: dict[str, Any], request_path: Path, dry_run: bool) -> dict[str, Any]:
    validate_update_request(request)
    projects = load_projects()
    slug = normalize_text(request['slug'])
    project = find_project(projects, slug)
    if not project:
        raise ValueError(f'Unknown project slug: {slug}')

    changed_fields: list[str] = []
    candidate = dict(project)
    for field in MUTABLE_FIELDS:
        if field in request:
            candidate[field] = normalize_text(request[field])
            changed_fields.append(field)
    candidate['updatedAt'] = request.get('updatedAt') or now_iso()
    validate_project(candidate)

    if dry_run:
        return build_receipt(
            action='update_project_meta',
            project=candidate,
            changed_fields=changed_fields,
            request_path=str(request_path),
            dry_run=True,
            rendered=False,
            project_created=False,
        )

    project.update({field: candidate[field] for field in changed_fields + ['updatedAt']})
    save_projects(projects)
    (ROOT / 'projects' / project['slug']).mkdir(parents=True, exist_ok=True)
    run_render(PROJECTS_PATH, EDITIONS_PATH)
    receipt = build_receipt(
        action='update_project_meta',
        project=project,
        changed_fields=changed_fields,
        request_path=str(request_path),
        dry_run=False,
        rendered=True,
        project_created=False,
    )
    receipt_path = RECEIPTS_DIR / f"project-update-{project['id']}-{project['updatedAt'][:19].replace(':', '-')}.json"
    dump_json(receipt_path, receipt)
    receipt['receiptPath'] = str(receipt_path)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description='Minimal project management interface for OpenClaw Newspaper')
    parser.add_argument('--action', required=True, choices=['create_project', 'update_project_meta'])
    parser.add_argument('--request', required=True, help='Path to JSON request file')
    parser.add_argument('--dry-run', action='store_true', help='Validate request and print receipt without writing source-of-truth')
    args = parser.parse_args()

    ensure_dirs()
    request_path = Path(args.request)
    request = json.loads(request_path.read_text(encoding='utf-8'))

    if args.action == 'create_project':
        receipt = create_project(request, request_path, args.dry_run)
    else:
        receipt = update_project_meta(request, request_path, args.dry_run)

    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
