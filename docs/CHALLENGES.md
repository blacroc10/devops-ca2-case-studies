# Challenges

Only problems that actually happened in this run.

## Docker CLI missing inside WSL

- Symptom: `docker` in this Ubuntu distro printed that the command could not be found and told me to turn on Docker Desktop WSL integration. `kubectl.exe` from Docker Desktop had no context and tried `localhost:8080`, which refused the connection. Kubernetes in Docker Desktop was not enabled.
- Cause: Docker Desktop 4.76 is running on Windows, but this distro is not integrated with it, so there is no `/var/run/docker.sock` and no local cluster.
- Fix: Installed `docker.io` 29.1.3 from Ubuntu apt and started the distro's `docker` systemd service. Local image builds and the kind cluster use that engine. Docker Desktop settings were not changed.

## Ansible check mode failed without python3-apt

- Symptom: the first `ansible-playbook --check` against the Ubuntu container failed with `python3-apt must be installed to use check mode`.
- Cause: the `ansible.builtin.apt` module can install its Python helper on a normal run, but check mode refuses to do that.
- Fix: installed `python3-apt` in the throwaway container, then reran `--check` and the two real applies. The WSL host was not the Ansible target.

## mermaid-cli could not write a PNG

- Symptom: `npx @mermaid-js/mermaid-cli` reported that `docs/diagrams/pipeline.mmd` does not exist.
- Cause: the `npx` on PATH is the Windows binary. It starts in `cmd.exe`, which cannot use the WSL path.
- Fix: none applied. The Mermaid source stays in `docs/diagrams/pipeline.mmd` and in the README. Screenshot the GitHub-rendered diagram.

## App metric label `service` was overwritten by the scrape

- Symptom: `http_requests_total` showed `service="catalog-service"` instead of `service="catalog"`, so the dashboard queries that filter on the application label matched nothing.
- Cause: Prometheus attaches the Kubernetes Service name as `service`, and the default `honorLabels: false` lets that target label replace the label the app emitted.
- Fix: set `honorLabels: true` on each ServiceMonitor endpoint so the application's `service` label is kept.

## A single /play during pod deletion still saw live recommendations

- Symptom: after `kubectl delete pod -l app=recommendations`, one immediate `GET /play` returned `"degraded": false` and the real title list. A direct call to recommendations a moment earlier had already failed.
- Cause: terminating pods were still on the Service endpoints and still answered. The fallback only runs when the call actually fails.
- Fix: the in-cluster load still counted `degraded=12` with `fail=0`. Scaling the deployment to 0 replicas and waiting until the pods were gone produced `"degraded": true` and the fallback list. That output is in `docs/evidence/netflix-chaos.txt`. The chaos script itself was not changed.

## Host RAM is under 8 GiB

- Symptom: `free -h` reports 7.5 GiB total.
- Cause: The WSL VM is sized under the 8 GiB the brief warned about for kube-prometheus-stack.
- Fix: `monitoring/values.yaml` turns alertmanager off, turns persistence off, disables control-plane component scrapes, and sets low memory requests.
- Follow-up: the Grafana container was OOMKilled once (exit 137) at a 256Mi limit while the pod was starting. The limit is now 512Mi and the chart's default dashboards are disabled so only the two case-study dashboards are loaded. After that change Grafana stayed up.
