#!/bin/bash
# Presentation-only, finite loopback preview. Never serve the repository root.
set -eu
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
test -f docs/professor_updates/research_review_20260928/review.html
mkdir -p outputs/professor-review-20260928
/usr/bin/python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 8768))
PY
D=$(mktemp -d /tmp/professor-review-http-XXXXXX)
cleanup() {
	rm -f -- "$D/research-review.html"
	rmdir -- "$D"
	/usr/bin/python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json
p = Path('outputs/professor-review-20260928/preview.json')
if p.exists():
    data = json.loads(p.read_text())
    data.update(status='ended', ended_utc=datetime.now(timezone.utc).isoformat())
    p.write_text(json.dumps(data, indent=2) + '\n')
PY
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
ln -s "$ROOT/docs/professor_updates/research_review_20260928/review.html" "$D/research-review.html"
/usr/bin/python3 - "$D" "$$" <<'PY'
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import json, sys
now = datetime.now(timezone.utc)
end = now + timedelta(seconds=7200)
data = dict(status='starting', directory=sys.argv[1], shell_pid=int(sys.argv[2]), bind='127.0.0.1', port=8768,
            started_utc=now.isoformat(), expires_utc=end.isoformat(), expires_singapore=end.astimezone(ZoneInfo('Asia/Singapore')).isoformat(),
            ttl_seconds=7200, owner_session='01a0e38c-dcd4-7dca-b5f1-641901a10a29', boot_restart=False,
            report='docs/professor_updates/research_review_20260928/review.html', url='http://localhost:8768/research-review.html')
Path('outputs/professor-review-20260928/preview.json').write_text(json.dumps(data, indent=2) + '\n')
print('Preview expires:', data['expires_singapore'], flush=True)
PY
if /usr/bin/timeout --foreground 7200 /usr/bin/python3 -u -m http.server 8768 --bind 127.0.0.1 --directory "$D"; then
	echo 'Preview stopped normally.'
else
	code=$?
	if [ "$code" -eq 124 ]; then echo 'Preview expired after two hours.'; else exit "$code"; fi
fi
