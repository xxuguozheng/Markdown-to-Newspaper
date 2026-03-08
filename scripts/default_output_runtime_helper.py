#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REQUESTS_DIR = ROOT / 'data' / 'requests'
PUBLISH_SCRIPT = ROOT / 'scripts' / 'publish_to_newspaper.py'
DEFAULT_PROJECT = 'OpenClaw-Newspaper-UI'
PUBLISH_KINDS = {'report', 'plan', 'status-update', 'research', 'briefing', 'long-answer'}
SKIP_KINDS = {'chat', 'small-talk', 'yes-no', 'tool-log', 'process-update', 'short-answer'}
PUBLISH_DENSITIES = {'longform', 'frontpage'}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def word_like_count(text: str) -> int:
    if not text:
        return 0
    parts = [p for p in text.replace('\n', ' ').split(' ') if p.strip()]
    return len(parts)


def char_count(text: str) -> int:
    return len(text or '')


def infer_should_publish(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    routing = payload.get('routing', {})
    if routing.get('skipPublish'):
        return False, ['routing.skipPublish=true']
    if routing.get('forcePublish'):
        return True, ['routing.forcePublish=true']

    output = payload.get('output', {})
    kind = output.get('kind', '').strip().lower()
    density = output.get('density', '').strip().lower()
    text = output.get('text', '') or ''
    summary = output.get('summary', '') or ''

    if kind in SKIP_KINDS:
        return False, [f'kind={kind} is configured to skip']
    if kind in PUBLISH_KINDS:
        reasons.append(f'kind={kind} is publish-worthy')
    if density in PUBLISH_DENSITIES:
        reasons.append(f'density={density} is archive-worthy')
    if char_count(text) >= 1200:
        reasons.append('text length >= 1200 chars')
    if word_like_count(summary) >= 20:
        reasons.append('summary is substantial')
    if output.get('html') or output.get('bodyHtml'):
        reasons.append('html/bodyHtml available')

    return bool(reasons), reasons or ['did not match publish rules']


def normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    project = payload.get('project', {})
    output = payload.get('output', {})
    source = payload.get('source', {})
    options = payload.get('options', {})

    body_html = output.get('bodyHtml') or output.get('html') or ''
    return {
        'project': {
            'slug': project.get('slug') or DEFAULT_PROJECT,
            'summary': project.get('summary', ''),
        },
        'edition': {
            'title': output.get('title') or '未命名长输出',
            'summary': output.get('summary', ''),
            'density': output.get('density', 'brief'),
            'tags': output.get('tags', []),
            'publishedAt': output.get('publishedAt') or now_iso(),
        },
        'content': {
            'bodyHtml': body_html,
        },
        'source': {
            'sessionId': source.get('sessionId', ''),
            'channel': source.get('channel', ''),
            'role': source.get('role', ''),
        },
        'options': {
            'updateProjectMeta': options.get('updateProjectMeta', False),
            'rebuildPortal': options.get('rebuildPortal', True),
            'rebuildProjectPage': options.get('rebuildProjectPage', True),
        },
    }


def build_chat_reply(payload: dict[str, Any], receipt: dict[str, Any] | None, should_publish: bool) -> dict[str, Any]:
    output = payload.get('output', {})
    summary = output.get('summary', '')
    if should_publish:
        return {
            'mode': 'summary-plus-links',
            'summary': summary,
            'editionUrl': receipt.get('editionUrl') if receipt else None,
            'projectUrl': receipt.get('projectUrl') if receipt else None,
            'portalUrl': receipt.get('portalUrl') if receipt else None,
            'suggestedText': f"{summary}\n\n报纸版：{receipt.get('editionUrl')}\n项目页：{receipt.get('projectUrl')}" if receipt else summary,
        }
    return {
        'mode': 'direct-chat',
        'summary': summary,
        'suggestedText': output.get('text', '') or summary,
    }


def save_request(request: dict[str, Any]) -> Path:
    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = request['edition']['publishedAt'][:19].replace(':', '-')
    path = REQUESTS_DIR / f"{request['project']['slug']}-{ts}.json"
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def publish_request(request_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ['python', str(PUBLISH_SCRIPT), '--request', str(request_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description='Runtime-facing helper for deciding whether a final output should be published to OpenClaw Newspaper')
    parser.add_argument('--input', required=True, help='Finalize payload JSON')
    parser.add_argument('--decide-only', action='store_true', help='Only decide and print normalized request / reply contract')
    parser.add_argument('--publish', action='store_true', help='Publish when routing rules say yes')
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    should_publish, reasons = infer_should_publish(payload)
    request = normalize_request(payload)
    result: dict[str, Any] = {
        'ok': True,
        'shouldPublish': should_publish,
        'reasons': reasons,
        'normalizedRequest': request,
        'receipt': None,
        'chatReply': None,
    }

    if should_publish and args.publish and not args.decide_only:
        request_path = save_request(request)
        receipt = publish_request(request_path)
        result['requestPath'] = str(request_path)
        result['receipt'] = receipt
        result['chatReply'] = build_chat_reply(payload, receipt, True)
    else:
        result['chatReply'] = build_chat_reply(payload, None, should_publish)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
