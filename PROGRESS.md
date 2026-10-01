# Progress

Deadline: midnight local time, 2026-10-02 00:00 EDT.
Last phase check: Thu Oct 1 12:07:01 EDT 2026. Well over 90 minutes remained.

RAM: 7.5 GiB. kube-prometheus-stack 91.8.2 is installed with alertmanager off, persistence off, and a 512Mi Grafana limit after one OOMKill at 256Mi.

## Phase 0 — Brief, deadline, environment audit

- [x] `reference/AGENT_BRIEF.md` saved locally (`reference/` is gitignored)
- [x] Assignment docx read
- [x] Tool audit. Docker Desktop has no WSL integration, so `docker.io` in this distro is the engine. kind cluster `ca2`.

## P0 — Amazon

- [x] Services, tests, images
- [x] Ansible check + two runs, second recap `changed=0` (`docs/evidence/ansible-run2.txt`)
- [x] Rolling update `ok=763 fail=0`, bad v3 stalled, undo back to v2, catalog pods untouched
- [x] Prometheus targets UP and queries return data

## P1 — Netflix

- [x] Same pipeline shape, Ansible `changed=0` on the second run
- [x] Rolling update `ok=669 fail=0`, bad revision, undo
- [x] Chaos dry-run, one real delete, load `ok=897 fail=0` with 12 degraded responses, scale-to-zero returned `"degraded": true`

## P2 — Write-up

- [x] Q1, Q2, README, architecture, pipeline, challenges, lessons, PPT guide, screenshot checklist, demo script
- [x] Mermaid source committed. PNG export failed (Windows npx cannot read the WSL path).

## P3 — Devpost

- [x] Public theme is a DSL contest. This repo was not submitted and no submission text was forced to fit. See `docs/DEVPOST_SUBMISSION.md`.

## Final

- [x] Pushed. Both latest Actions runs are green (amazon `36890908602`, netflix `36890908595`)
- [x] STATUS.md
