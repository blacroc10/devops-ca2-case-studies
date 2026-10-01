# Status

Repo: https://github.com/blacroc10/devops-ca2-case-studies

Latest Actions runs, both green, all three jobs:

| Workflow | Run | Result |
| --- | --- | --- |
| amazon-ci-cd | https://github.com/blacroc10/devops-ca2-case-studies/actions/runs/36890908602 | success |
| netflix-ci-cd | https://github.com/blacroc10/devops-ca2-case-studies/actions/runs/36890908595 | success |

The push before that failed in `deploy` only (kind v0.31.0 could not init Kubernetes 1.37). That is fixed and recorded in `docs/CHALLENGES.md`. Screenshot the green runs, not those.

Checked at Thu Oct 1 12:20 EDT 2026. Deadline is midnight. Local kind cluster `ca2` was still up when this was written.

| Task | Amazon | Netflix | Evidence |
| --- | --- | --- | --- |
| T1 GitHub Actions | Done, verified | Done, verified | green runs above; `docs/diagrams/pipeline.mmd` |
| T2 Ansible | Done, verified | Done, verified | `docs/evidence/ansible-run2.txt` and `netflix-ansible-run2.txt` (`changed=0`) |
| T3 Docker and Kubernetes | Done, verified | Done, verified | `docs/evidence/amazon-rollout.txt` (`ok=763 fail=0`), `netflix-rollout.txt` (`ok=669 fail=0`) |
| T4 Prometheus and Grafana | Done, verified | Done, verified | `docs/evidence/prometheus-queries.txt` (12 app targets UP), dashboards loaded by the sidecar |
| T5 Write-up | Done | Done | `docs/answers/`, `docs/PPT_GUIDE.md` (you still write the slides) |
| Chaos | — | Done, verified | `docs/evidence/netflix-chaos.txt` (`ok=897 fail=0`, then `"degraded": true`) |
| Devpost | Not submitted | Not submitted | Theme is a DSL contest. See `docs/DEVPOST_SUBMISSION.md` |

## What you still do

1. Screenshots in `docs/SCREENSHOT_CHECKLIST.md`. `scripts/demo.sh` prints the banner and the live reads. The long demos are the other scripts in `scripts/` if you want to retake them.
2. The 4–5 slides, from `docs/PPT_GUIDE.md`, in your own words.
3. A demo video, if you want one. I did not record one.
4. Port-forward Grafana when you take the dashboard shots. Check the port is free first.

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
kubectl -n monitoring get secret monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

User `admin`. Do not paste the password into the repo. Time range: last 15 minutes. Run `scripts/load.sh` against a port-forward of the service if the panels look empty.

5. Devpost: do not submit this repository to Syntax Summit. The public theme is to build a domain-specific language. Snippets of the deadline disagree (one rules snippet says 5 Sep 2026, which is already past; the schedule snippet says 14 Jan 2027). Open the page yourself before you decide. Nothing was submitted.
