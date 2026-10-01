# Q1. Netflix

## What the 2008 outage exposed

In August 2008 a database corruption stopped Netflix from shipping DVDs for three days. The case study uses that outage to show how brittle a monolith is, and the public history of the company supports the same reading. One corrupted database was enough to halt a business process that the rest of the system could not route around.

That design failed in four ways. The shipment path depended on one database, so corruption stopped the flow instead of one feature. Callers inside the same process had no boundary where they could time out and continue. Repairing the data and restoring the application were the same event, so recovery was slow. The DVD path and every other workload had to grow together, and a bad change shipped with everything else.

## What DevOps changed

Netflix later moved the platform to Amazon Web Services and split it into services that deploy and fail separately. A smaller blast radius only helps if the caller expects the callee to disappear. Chaos Monkey, and then the wider Simian Army, killed production instances on purpose so teams would find the code that still assumed the process would stay up. The principles that came out of that work are plain: state what steady behavior should look like, inject a real event such as instance death, run it against a system that resembles production, and automate the experiment. The aim is to make an outage boring, not to cause one.

## What this repository actually did

playback-service calls recommendations-service with a 0.4 second timeout. When recommendations was scaled to zero replicas, `GET /play` still returned HTTP 200 with `"degraded": true` and the fallback titles Stranger Things, The Crown, and Narcos. `netflix/chaos/chaos_monkey.py` refuses every namespace other than `netflix-demo` and only selects pods labeled `chaos=enabled`. A dry run printed a pod and deleted nothing. With `--execute` it deleted one playback pod, and Kubernetes created a replacement while the other playback pods kept their original start time. A 50 second load recorded `ok=897 fail=0`, of which 12 responses were degraded. Those counts are from `docs/evidence/netflix-chaos.txt`.

A rolling update of playback from v1 to v2 did not touch the recommendations pods: same start times, zero restarts. The in-cluster health loop recorded `ok=669 fail=0`. A bad revision that failed its readiness probe sat unready while `maxUnavailable: 0` kept the previous pods in the Service, which continued to report version v2. `kubectl rollout undo` restored v2. Ansible was applied, not merely described: the second run against a throwaway Ubuntu container ended `changed=0`, and it created the `playback` group, the `playbacksvc` user, directories, a Jinja2 config, and a copy of the app.

## Resilience and scale, without exaggeration

Resilience here means a dependency can vanish without taking the caller down, and a deleted pod is replaced by the control plane. Scalability means each service has its own replica count and its own rollout. Three replicas on one kind node demonstrate that mechanism. They do not demonstrate unbounded scale.
