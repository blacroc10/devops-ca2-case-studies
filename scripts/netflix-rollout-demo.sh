#!/usr/bin/env bash
set -u
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
export PATH="$HOME/.local/bin:$PATH"
NS=netflix-demo

echo "===== recommendations pods before playback rollout ====="
kubectl -n "$NS" get pods -l app=recommendations -o custom-columns=NAME:.metadata.name,START:.status.startTime,RESTARTS:.status.containerStatuses[0].restartCount

kubectl -n "$NS" delete pod traffic --ignore-not-found --wait=true >/dev/null
kubectl -n "$NS" run traffic \
  --image=netflix-playback:v1 \
  --image-pull-policy=IfNotPresent \
  --restart=Never \
  --command -- python -c '
import time, urllib.request
ok = fail = 0
end = time.time() + 35
url = "http://playback-service.netflix-demo.svc.cluster.local:8080/health"
while time.time() < end:
    try:
        urllib.request.urlopen(url, timeout=2)
        ok += 1
    except Exception:
        fail += 1
    time.sleep(0.05)
print("ok=%s fail=%s" % (ok, fail), flush=True)
'
kubectl -n "$NS" wait --for=condition=Ready pod/traffic --timeout=60s

echo "===== roll playback v1 -> v2 ====="
kubectl -n "$NS" patch deployment playback --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/image","value":"netflix-playback:v2"},{"op":"replace","path":"/spec/template/spec/containers/0/env/0/value","value":"v2"}]'
kubectl -n "$NS" rollout status deployment/playback --timeout=180s
kubectl -n "$NS" exec deploy/playback -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/version", timeout=5).read().decode())'

echo "===== recommendations pods after ====="
kubectl -n "$NS" get pods -l app=recommendations -o custom-columns=NAME:.metadata.name,START:.status.startTime,RESTARTS:.status.containerStatuses[0].restartCount

echo "===== traffic ====="
kubectl -n "$NS" logs -f pod/traffic

echo "===== bad v3 ====="
kubectl -n "$NS" set env deployment/playback APP_VERSION=v3 FAIL_READY=1
set +e
kubectl -n "$NS" rollout status deployment/playback --timeout=30s
echo "rollout_status_exit=$?"
set -e
kubectl -n "$NS" get pods -l app=playback
kubectl -n "$NS" exec deploy/recommendations -- python -c 'import urllib.request; print(urllib.request.urlopen("http://playback-service.netflix-demo.svc.cluster.local:8080/version", timeout=5).read().decode())'

echo "===== rollback ====="
kubectl -n "$NS" rollout undo deployment/playback
kubectl -n "$NS" rollout status deployment/playback --timeout=180s
kubectl -n "$NS" exec deploy/playback -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/version", timeout=5).read().decode()); print(urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5).read().decode())'
kubectl -n "$NS" delete pod traffic --ignore-not-found --wait=false >/dev/null
