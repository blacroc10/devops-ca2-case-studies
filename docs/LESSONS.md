# Lessons learned

These are from this run, not from a template.

Independent deployment is visible in pod start times. After orders moved to v2, catalog's three pods were still the ones that had started at `2026-10-01T15:58:51Z`. That is a better check than a screenshot of a YAML file, because it shows the control plane did not restart the other service.

`maxUnavailable: 0` is what kept the old pods serving during the bad revision. The new pod was Running and not Ready, `rollout status` timed out, and the Service still returned v2. Rollback is a separate step. The probes do not undo the rollout by themselves.

A timeout plus a fallback is enough to keep HTTP success at 100 percent while a dependency is gone. The Netflix load recorded `fail=0` and `degraded=12`. Scaling recommendations to zero produced an explicit `"degraded": true` body. Deleting pods and immediately calling `/play` once did not, because terminating pods were still answering. The measurement has to wait until the endpoints are actually gone.

Check mode is not a free preview of an apt-based playbook. It refuses to run until `python3-apt` is installed. The second real run is the idempotency evidence (`changed=0`), not the check run, which correctly reports that it would change a fresh host.

The WSL distro did not inherit Docker Desktop's engine. Installing `docker.io` inside the distro was enough for kind. Leaving Docker Desktop's Kubernetes checkbox off avoided two clusters fighting over the same idea of "local".

A 7.5 GiB VM can run this cluster only if Prometheus is trimmed before the install, not after it has already requested several gigabytes. Alertmanager, persistent volumes, and the control-plane component scrapes were turned off up front.

GitHub Actions majors move. Pinning `checkout@v4` because it was current in an older course would have brought back the Node 20 warning this assignment asked to avoid. The versions in the workflows were read from the current releases instead.
