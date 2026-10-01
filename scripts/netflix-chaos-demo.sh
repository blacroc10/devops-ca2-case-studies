#!/usr/bin/env bash
# Self-healing plus graceful degradation while playback stays up.
set -u
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
export PATH="$HOME/.local/bin:$PATH"
NS=netflix-demo
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "===== pods before ====="
kubectl -n "$NS" get pods -o custom-columns=NAME:.metadata.name,START:.status.startTime,LABELS:.metadata.labels.chaos,READY:.status.containerStatuses[0].ready

echo "===== chaos monkey dry-run ====="
python3 "$ROOT/netflix/chaos/chaos_monkey.py" --namespace "$NS"
echo "===== refuse other namespace ====="
python3 "$ROOT/netflix/chaos/chaos_monkey.py" --namespace amazon-demo || true

echo "===== start playback load ====="
kubectl -n "$NS" delete pod chaos-load --ignore-not-found --wait=true >/dev/null
kubectl -n "$NS" run chaos-load \
  --image=netflix-playback:v1 \
  --image-pull-policy=IfNotPresent \
  --restart=Never \
  --command -- python -c '
import json, time, urllib.request
ok = fail = degraded = 0
end = time.time() + 50
url = "http://playback-service.netflix-demo.svc.cluster.local:8080/play"
while time.time() < end:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            body = json.loads(resp.read().decode())
        if resp.status == 200:
            ok += 1
        else:
            fail += 1
        if body.get("degraded"):
            degraded += 1
    except Exception:
        fail += 1
    time.sleep(0.05)
print("ok=%s fail=%s degraded=%s" % (ok, fail, degraded), flush=True)
'
kubectl -n "$NS" wait --for=condition=Ready pod/chaos-load --timeout=60s
sleep 3

echo "===== chaos monkey execute ====="
python3 "$ROOT/netflix/chaos/chaos_monkey.py" --namespace "$NS" --execute
sleep 2
echo "===== delete recommendations pods to force the fallback ====="
kubectl -n "$NS" delete pod -l app=recommendations --wait=false
sleep 3
echo "===== one playback call during the outage ====="
kubectl -n "$NS" exec deploy/playback -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/play", timeout=5).read().decode())' || true

echo "===== wait for self-heal ====="
kubectl -n "$NS" rollout status deployment/playback --timeout=180s
kubectl -n "$NS" rollout status deployment/recommendations --timeout=180s
echo "===== pods after ====="
kubectl -n "$NS" get pods -o custom-columns=NAME:.metadata.name,START:.status.startTime,RESTARTS:.status.containerStatuses[0].restartCount
echo "===== playback after recovery ====="
kubectl -n "$NS" exec deploy/playback -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/play", timeout=5).read().decode())'
echo "===== load result ====="
kubectl -n "$NS" logs -f pod/chaos-load
