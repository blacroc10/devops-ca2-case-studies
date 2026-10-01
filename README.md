# DevOps CA-II: Amazon and Netflix case studies

Shubhankar Sarangi, PRN 23070122206. Two case studies from the CA-II brief: Amazon (independent services) and Netflix (graceful degradation and chaos). The written answers are in `docs/answers/`.

## What is in the cluster

One kind cluster, `ca2`, three namespaces:

| Namespace | Workload |
| --- | --- |
| `amazon-demo` | catalog and orders |
| `netflix-demo` | playback and recommendations |
| `monitoring` | kube-prometheus-stack 91.8.2, trimmed |

orders calls catalog over cluster DNS. playback calls recommendations with a 0.4s timeout and, on failure, returns `"degraded": true`.

## Prerequisites that were missing on this machine

Ubuntu 26.04 in WSL2, 7.5 GiB RAM. Docker Desktop is installed on Windows but this distro is not integrated with it. The tools actually used:

- `docker.io` from apt (the distro engine, not Docker Desktop)
- `kubectl` 1.37.1, `kind` 0.33.0, `helm` 4.3.0 in `~/.local/bin`
- `ansible` from apt, executed inside a throwaway `ubuntu:24.04` container so the WSL host is not the target
- Python 3.14 on the host for unit tests; the images use Python 3.12

```bash
export PATH="$HOME/.local/bin:$PATH"
export KUBECONFIG="$HOME/.kube/config"
```

## Reproduce the apps

```bash
python3 -m venv .venv
.venv/bin/pip install flask==3.1.3 prometheus-client==0.26.0 gunicorn==26.2.0 pytest ruff
root="$PWD"
for d in amazon/services/catalog amazon/services/orders netflix/services/playback netflix/services/recommendations; do
  (cd "$d" && "$root/.venv/bin/ruff" check . && "$root/.venv/bin/pytest" -q)
done
```

Images:

```bash
sudo docker build -t amazon-catalog:v1 amazon/services/catalog
sudo docker build -t amazon-orders:v1 amazon/services/orders
sudo docker tag amazon-catalog:v1 amazon-catalog:v2
sudo docker tag amazon-orders:v1 amazon-orders:v2
sudo docker build -t netflix-playback:v1 netflix/services/playback
sudo docker build -t netflix-recommendations:v1 netflix/services/recommendations
sudo docker tag netflix-playback:v1 netflix-playback:v2
sudo docker tag netflix-recommendations:v1 netflix-recommendations:v2
```

Cluster:

```bash
sudo kind create cluster --name ca2 --image kindest/node:v1.37.0 --config cluster/kind-config.yaml --kubeconfig "$HOME/.kube/config"
sudo chown "$USER:$USER" "$HOME/.kube/config"
sudo kind load docker-image amazon-catalog:v1 amazon-catalog:v2 amazon-orders:v1 amazon-orders:v2 \
  netflix-playback:v1 netflix-playback:v2 netflix-recommendations:v1 netflix-recommendations:v2 --name ca2
kubectl apply -f amazon/k8s/namespace.yaml -f amazon/k8s/catalog.yaml -f amazon/k8s/orders.yaml
kubectl apply -f netflix/k8s/namespace.yaml -f netflix/k8s/playback.yaml -f netflix/k8s/recommendations.yaml
```

Ansible, against a container you create, not against the host:

```bash
sudo docker run -d --name ca2-ansible-amazon ubuntu:24.04 sleep infinity
sudo docker exec ca2-ansible-amazon apt-get update
sudo docker exec ca2-ansible-amazon apt-get install -y python3 ansible python3-apt
sudo docker cp amazon ca2-ansible-amazon:/work
sudo docker exec -w /work/ansible ca2-ansible-amazon ansible-playbook -i inventory.ini playbook.yml --check
sudo docker exec -w /work/ansible ca2-ansible-amazon ansible-playbook -i inventory.ini playbook.yml
sudo docker exec -w /work/ansible ca2-ansible-amazon ansible-playbook -i inventory.ini playbook.yml
```

Repeat with `netflix` and container name `ca2-ansible-netflix`. The second apply should report `changed=0`.

Demos: `scripts/amazon-rollout-demo.sh`, `scripts/netflix-rollout-demo.sh`, `scripts/netflix-chaos-demo.sh`, `scripts/demo.sh`.

## Monitoring

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --version 91.8.2 --namespace monitoring --create-namespace \
  -f monitoring/values.yaml --timeout 12m --wait
kubectl apply -f amazon/monitoring/servicemonitor.yaml -f netflix/monitoring/servicemonitor.yaml
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k monitoring/
```

`values.yaml` turns alertmanager off, turns persistence off, and sets low memory requests because this VM has 7.5 GiB.

Check that nothing is already bound, then port-forward. On this machine 8080 was free in WSL; the forwards below still use other ports so they do not collide with a process you start later.

```bash
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Grafana admin user is `admin`. Read the password when you need it. Do not write it into a file or a commit:

```bash
kubectl -n monitoring get secret monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

If those Service names differ, `kubectl -n monitoring get svc` is the source of truth. Prometheus targets: `http://127.0.0.1:9090/targets`. Dashboards: Amazon overview and Netflix overview, time range last 15 minutes.

Generate traffic after the port-forward to a service (pick a free local port):

```bash
kubectl -n amazon-demo port-forward svc/catalog-service 18080:8080
COUNT=40 scripts/load.sh http://127.0.0.1:18080 /products
```

## GitHub Actions

`.github/workflows/amazon-ci-cd.yml` and `netflix-ci-cd.yml`. Push to `main` runs test, pushes to GHCR, and deploys on a kind cluster in the runner. The action versions used are checkout v7, setup-python v7, setup-buildx v4, login v4, build-push v7, and kind-action v1, all on Node 24.

## Docs

`docs/ARCHITECTURE.md`, `docs/PIPELINE.md`, `docs/CHALLENGES.md`, `docs/LESSONS.md`, `docs/PPT_GUIDE.md`, `docs/SCREENSHOT_CHECKLIST.md`. Evidence from this run is in `docs/evidence/`.
