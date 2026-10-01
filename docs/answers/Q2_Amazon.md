# Q2. Amazon

## What the monolith was doing

In the early 2000s Amazon's retail application was still a monolith. The case study states the operational result directly: frequent outages and slow feature releases, with customer experience and revenue on the same critical path as every code change. A single deployable unit forces every team through one release. A defect in one area, or a long test cycle for one area, holds every other area. Outages are also shared, because the process that takes the order is the process that serves the catalog.

## Two-pizza teams and service boundaries

The two-pizza rule, associated with Jeff Bezos, keeps a team small enough to be fed by two pizzas so that it can own one problem. Ownership has to match the architecture. Amazon's service-oriented shift drew the boundary at the API: another team may call the service, and may not reach into its database or its deploy. Werner Vogels' line "you build it, you run it" puts the pager with the people who shipped the change, which is what makes a small team careful about the releases it can now do on its own.

That is the cultural half of the case study's "continuous innovation" claim. The case study cites an average deploy every 11.7 seconds. This project did not measure that rate, and the figure is used only as cited there. The architecture is what makes a one-service release possible without a company-wide train. The average is a reported outcome of many teams doing that, not a property of any single pipeline.

## What this repository actually did

catalog and orders are separate Flask services, separate Dockerfiles, separate Deployments, and separate jobs in `.github/workflows/amazon-ci-cd.yml`. orders calls catalog only over Kubernetes DNS (`catalog-service.amazon-demo.svc.cluster.local`). It does not import catalog's code. Before a rollout, the three catalog pods had all started at `2026-10-01T15:58:51Z` with zero restarts. After orders moved from image `amazon-orders:v1` and `APP_VERSION=v1` to `amazon-orders:v2` and `APP_VERSION=v2`, those catalog start times and restart counts were unchanged, and orders reported `"version":"v2"`. An in-cluster loop against orders `/health` during that rollout recorded `ok=763 fail=0` (`docs/evidence/amazon-rollout.txt`).

A deliberately bad revision set `FAIL_READY=1`, so `/health` returned 503 and the new pod stayed unready. `maxUnavailable: 0` kept the three v2 pods serving, and the Service still returned version v2. `rollout status` timed out. `kubectl rollout undo` restored v2 and a healthy `/health`. Ansible, aimed at a throwaway Ubuntu container so the WSL host was not modified, created the group `twopizza` and the user `catalogsvc`, directories with explicit modes, a Jinja2 config, and copies of the app files. The second run's recap was `changed=0`.

## What that shows

Independent deployment is the concrete answer to a slow, shared release train: one team can roll orders and leave catalog's pods untouched. The bad revision shows why "you build it, you run it" needs a probe and a rollback, not only a smaller team. None of these local runs is evidence for the 11.7 second figure.
