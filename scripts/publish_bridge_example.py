#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUESTS_DIR = ROOT / 'data' / 'requests'
PUBLISH_SCRIPT = ROOT / 'scripts' / 'publish_to_newspaper.py'


def normalize(payload: dict) -> dict:
    return {
        'project': {'slug': payload['project']},
        'edition': {
            'title': payload['title'],
            'summary': payload.get('summary', ''),
            'density': payload.get('density', 'brief'),
            'tags': payload.get('tags', []),
            'publishedAt': payload.get('publishedAt') or datetime.now().astimezone().isoformat(timespec='seconds'),
        },
        'content': {'bodyHtml': payload.get('bodyHtml') or payload.get('html') or ''},
        'source': payload.get('source', {}),
        'options': {
            'updateProjectMeta': False,
            'rebuildPortal': True,
            'rebuildProjectPage': True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Example bridge from default output payload to PublishRequest')
    parser.add_argument('--input', required=True, help='Loose input payload json')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    request = normalize(payload)
    if args.dry_run or not args.publish:
        print(json.dumps(request, ensure_ascii=False, indent=2))
        return

    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REQUESTS_DIR / f"{request['project']['slug']}-{request['edition']['publishedAt'][:19].replace(':','-')}.json"
    out.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    subprocess.run(['python', str(PUBLISH_SCRIPT), '--request', str(out)], check=True)


if __name__ == '__main__':
    main()
