#!/usr/bin/env bash
set -euo pipefail

UNIT="$HOME/.config/systemd/user/openclaw-newspaper.service"
if [[ ! -f "$UNIT" ]]; then
  echo "unit file missing: $UNIT" >&2
  exit 1
fi

systemctl --user daemon-reload
systemctl --user enable --now openclaw-newspaper.service
systemctl --user status openclaw-newspaper.service --no-pager --lines=20 || true

echo
echo "OpenClaw Newspaper is expected at: http://127.0.0.1:39117/site/index.html"
