# Slide guide

Write these in your own words. Do not paste the case-study answers in as the slide text. Four content slides plus an optional title slide is enough. Cover both Amazon and Netflix on each slide, with Amazon first.

## Optional title

- Your name, PRN 23070122206, Symbiosis Institute of Technology, DevOps CA-II.
- One line: Q2 Amazon and Q1 Netflix, monolith to independently deployed services.
- No diagram.

Speaker notes: say you implemented both, and that the 11.7 second figure is cited from the case study rather than measured here.

## Slide 1 — Architecture

Purpose: show the two systems and where a call crosses a service boundary.

Cover:

- Amazon: catalog and orders, orders calls catalog over cluster DNS, separate Deployments.
- Netflix: playback calls recommendations with a 0.4s timeout and returns `"degraded": true` instead of failing the request.
- One kind cluster, namespaces `amazon-demo` and `netflix-demo`.

Put the diagram from `docs/ARCHITECTURE.md` (or a screenshot of the GitHub-rendered Mermaid) on this slide. A `kubectl get pods -n amazon-demo` and `-n netflix-demo` screenshot can sit beside it if you have room.

Speaker notes:

- Catalog's pod start times did not change when orders rolled.
- Playback stayed HTTP 200 when recommendations was scaled to zero.

## Slide 2 — Pipeline

Purpose: the three jobs, and that deploy is real.

Cover:

- Trigger: push to `main`, path-filtered per case study.
- test (ruff, pytest), build-push (GHCR, sha and latest), deploy (kind, rollout status, `/health`, undo on failure).
- Point at the green run, not at a queued one.

Use the Mermaid in `docs/PIPELINE.md` and the screenshot of the Actions graph with all three jobs green, once for Amazon and once for Netflix.

Speaker notes:

- Pull requests test and build, and do not deploy.
- Local manifests use `IfNotPresent` plus `kind load`; CI pulls the same tags from GHCR and loads them the same way.

## Slide 3 — Tasks 2, 3, and 4

Purpose: evidence, three pictures.

Cover:

- Ansible: second recap `changed=0`. Amazon group `twopizza`, Netflix group `playback`. The playbook ran in a throwaway Ubuntu container.
- Kubernetes: rolling update with `fail=0`, bad revision stuck not-ready, `rollout undo` back to v2. Mention the Netflix chaos line `ok=897 fail=0` and the `"degraded": true` body.
- Monitoring: Prometheus targets UP, and the Grafana panels for uptime, latency, and error rate with the time range set so the load is visible.

Place three screenshots: Ansible run 2, the stalled bad rollout, the Grafana dashboard. If a fourth fits, use the chaos pod list that shows a new start time.

Speaker notes:

- `maxUnavailable: 0` is why the old pods kept serving.
- The chaos script dry-run deletes nothing, and it refuses any namespace other than `netflix-demo`.

## Slide 4 — Challenges and lessons

Purpose: only things that happened, and what you would repeat.

Cover, in your words, from `docs/CHALLENGES.md` and `docs/LESSONS.md`:

- Docker Desktop was running, but this WSL distro had no docker CLI and no Kubernetes. `docker.io` inside the distro was the fix.
- Ansible `--check` failed until `python3-apt` was installed.
- RAM is 7.5 GiB, so the Prometheus stack was trimmed before install.
- A single `/play` during pod deletion still saw live recommendations; the load test and a scale-to-zero were the measurements that showed degradation.
- Lesson: prove an independent deploy with the other service's pod start time, and prove a safe rollout with a failed request count of zero.

Do not include the classmate deck's leftover template slides, and do not say "infinite scalability" or that this cluster deploys every 11.7 seconds.

Speaker notes:

- Say which evidence file backs each claim (`docs/evidence/`).
- If a GitHub Actions run is red at the time you present, say so. Do not crop a failure out.
