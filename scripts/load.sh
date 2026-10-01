#!/usr/bin/env bash
# Mixed traffic so latency and error-rate panels have something to show.
# Usage: scripts/load.sh http://127.0.0.1:18080 [/extra-path]
set -euo pipefail
BASE="${1:?base URL required}"
EXTRA="${2:-}"
COUNT="${COUNT:-80}"
ok=0
fail=0
for i in $(seq 1 "$COUNT"); do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$BASE/health" || echo 000)
  if [[ "$code" =~ ^2 ]]; then ok=$((ok + 1)); else fail=$((fail + 1)); fi
  if [[ -n "$EXTRA" ]]; then
    curl -s -o /dev/null --max-time 5 "$BASE$EXTRA" || true
  fi
  if (( i % 8 == 0 )); then
    curl -s -o /dev/null --max-time 5 "$BASE/error" || true
  fi
  if (( i % 6 == 0 )); then
    curl -s -o /dev/null --max-time 8 "$BASE/slow?ms=250" || true
  fi
done
echo "health_ok=$ok health_fail=$fail base=$BASE"
