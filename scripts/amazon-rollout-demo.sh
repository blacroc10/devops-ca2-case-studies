#!/usr/bin/env bash
# Rolling update, failed release, and rollback for orders. Catalog stays put.
set -u
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
export PATH="$HOME/.local/bin:$PATH"
NS=amazon-demo

echo "===== catalog pods before orders rollout ====="
kubectl -n "$NS" get pods -l app=catalog -o custom-columns=NAME:.metadata.name,START:.status.startTime,RESTARTS:.status.containerStatuses[0].restartCount

echo "===== start traffic against orders ====="
kubectl -n "$NS" delete pod traffic --ignore-not-found --wait=true >/dev/null
kubectl -n "$NS" run traffic \
  --image=amazon-catalog:v1 \
  --image-pull-policy=IfNotPresent \
  --restart=Never \
  --command -- python -c '
import time, urllib.request
ok = fail = 0
end = time.time() + 40
while time.time() < end:
    try:
        urllib.request.urlopen("http://orders-service.amazon-demo.svc.cluster.local:8080/health", timeout=2)
        ok += 1
    except Exception:
        fail += 1
    time.sleep(0.05)
print("ok=%s fail=%s" % (ok, fail), flush=True)
'
kubectl -n "$NS" wait --for=condition=Ready pod/traffic --timeout=60s

echo "===== roll orders v1 -> v2 ====="
kubectl -n "$NS" patch deployment orders --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/image","value":"amazon-orders:v2"},{"op":"replace","path":"/spec/template/spec/containers/0/env/0/value","value":"v2"}]'
kubectl -n "$NS" rollout status deployment/orders --timeout=180s
kubectl -n "$NS" rollout history deployment/orders

echo "===== catalog pods after orders rollout ====="
kubectl -n "$NS" get pods -l app=catalog -o custom-columns=NAME:.metadata.name,START:.status.startTime,RESTARTS:.status.containerStatuses[0].restartCount
echo "===== orders version ====="
kubectl -n "$NS" exec deploy/orders -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/version", timeout=5).read().decode())'

echo "===== traffic result ====="
kubectl -n "$NS" logs -f pod/traffic

echo "===== bad v3 (readiness fails) ====="
kubectl -n "$NS" set env deployment/orders APP_VERSION=v3 FAIL_READY=1
set +e
kubectl -n "$NS" rollout status deployment/orders --timeout=30s
echo "rollout_status_exit=$?"
set -e
kubectl -n "$NS" get pods -l app=orders -o wide
echo "===== service still answers on the previous pods ====="
kubectl -n "$NS" exec deploy/catalog -- python -c 'import urllib.request; print(urllib.request.urlopen("http://orders-service.amazon-demo.svc.cluster.local:8080/version", timeout=5).read().decode())'

echo "===== rollback ====="
kubectl -n "$NS" rollout undo deployment/orders
kubectl -n "$NS" rollout status deployment/orders --timeout=180s
kubectl -n "$NS" rollout history deployment/orders
kubectl -n "$NS" exec deploy/orders -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/version", timeout=5).read().decode()); print(urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5).read().decode())'
kubectl -n "$NS" get pods -o wide
