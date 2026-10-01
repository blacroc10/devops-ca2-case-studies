#!/usr/bin/env bash
# Live reads for screenshots. Does not roll out or delete pods.
set -u
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
export PATH="$HOME/.local/bin:$PATH"
echo "Shubhankar Sarangi | PRN 23070122206 | $(date)"
echo
echo "===== nodes ====="
kubectl get nodes
echo
echo "===== amazon-demo ====="
kubectl get pods,svc -n amazon-demo -o wide
echo
echo "===== netflix-demo ====="
kubectl get pods,svc -n netflix-demo -o wide
echo
echo "===== catalog /health and orders /version ====="
kubectl -n amazon-demo exec deploy/catalog -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5).read().decode())'
kubectl -n amazon-demo exec deploy/orders -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/version", timeout=5).read().decode()); print(urllib.request.urlopen("http://catalog-service.amazon-demo.svc.cluster.local:8080/products", timeout=5).read().decode())'
echo
echo "===== playback /play ====="
kubectl -n netflix-demo exec deploy/playback -- python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8080/play?title=Wednesday", timeout=5).read().decode())'
echo
echo "===== chaos monkey dry-run ====="
python3 "$(dirname "$0")/../netflix/chaos/chaos_monkey.py"
echo
echo "Re-run the long demos only when you want new evidence:"
echo "  scripts/amazon-rollout-demo.sh"
echo "  scripts/netflix-rollout-demo.sh"
echo "  scripts/netflix-chaos-demo.sh"
