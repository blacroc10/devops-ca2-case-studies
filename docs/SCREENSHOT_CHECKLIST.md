# Screenshot checklist

Save files under a folder you do not commit if they are only for the PPT. The terminal must show the command and the output. Where a timestamp, namespace, or GitHub username matters, it has to be in the frame.

Run `scripts/demo.sh` for the banner and the live reads. The longer demos are the scripts named below; their saved output is already in `docs/evidence/` if you would rather screenshot the file than re-run them.

1. `01-actions-amazon-list.png` — GitHub Actions tab for `blacroc10/devops-ca2-case-studies`, workflow `amazon-ci-cd`, the run list. The green run and your username must be visible.
2. `02-actions-amazon-graph.png` — open that green run. The graph must show test, build-push, and deploy. All green.
3. `03-actions-netflix-list.png` — same for `netflix-ci-cd`.
4. `04-actions-netflix-graph.png` — green graph with the three jobs.
5. `05-workflow-file.png` — the workflow file on GitHub (`amazon-ci-cd.yml` or `netflix-ci-cd.yml`), scrolled so the three job names show.
6. `06-ansible-amazon-run1.png` — `docs/evidence/ansible-run1.txt` or a re-run. PLAY RECAP `changed=8` (first apply) visible.
7. `07-ansible-amazon-run2.png` — `docs/evidence/ansible-run2.txt`. PLAY RECAP `changed=0`.
8. `08-ansible-netflix-run2.png` — `docs/evidence/netflix-ansible-run2.txt`, `changed=0`, and the verify block with user `playbacksvc` if you can fit it.
9. `09-docker-build.png` — `sudo docker build -t amazon-catalog:v1 amazon/services/catalog` ending in `Successfully tagged`.
10. `10-docker-images.png` — `sudo docker images` showing the four service images.
11. `11-health-browser.png` — port-forward catalog (see README for the free port) and open `/health` in the browser. JSON `"status":"ok"` and the URL bar.
12. `12-kubectl-pods.png` — `kubectl get pods,svc -n amazon-demo` and the same for `netflix-demo`. Namespace and Ready 1/1 visible. Banner from `scripts/demo.sh` can be the line above.
13. `13-rolling-update.png` — `docs/evidence/amazon-rollout.txt`: `ok=763 fail=0`, orders version v2, catalog start times unchanged.
14. `14-bad-release.png` — same file: `rollout_status_exit=1` and a pod `0/1 Running` next to pods that are `1/1`.
15. `15-rollback.png` — version back to v2 and `/health` ok after `rollout undo`.
16. `16-chaos-self-heal.png` — `docs/evidence/netflix-chaos.txt`: dry-run, the deleted pod, a new pod start time, `ok=897 fail=0`, and the `"degraded": true` body from the scale-to-zero section.
17. `17-prometheus-targets.png` — Prometheus `/targets` (port-forward in the README) filtered to the app jobs, state UP.
18. `18-grafana-amazon.png` — Amazon dashboard, time range last 15 minutes, traffic and an error spike visible, uptime and latency panels filled.
19. `19-grafana-netflix.png` — same for the Netflix dashboard.
20. `20-ghcr.png` — `https://github.com/blacroc10?tab=packages` or the package page for `amazon-catalog`. Your username visible.
21. `21-devpost.png` — only if you submit something that actually matches that hackathon. This DevOps repo is not a DSL. Do not screenshot a forced submission.

Netflix rolling-update numbers, if you want a pair to the Amazon ones, are in `docs/evidence/netflix-rollout.txt` (`ok=669 fail=0`).
