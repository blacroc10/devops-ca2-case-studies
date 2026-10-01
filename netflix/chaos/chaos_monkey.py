#!/usr/bin/env python3
"""Delete one random pod in namespace netflix-demo that carries chaos=enabled.

Dry-run unless --execute is passed. Refuses every other namespace.
"""

import argparse
import random
import subprocess
import sys

ALLOWED_NAMESPACE = "netflix-demo"
LABEL = "chaos=enabled"


def list_pods(namespace):
    if namespace != ALLOWED_NAMESPACE:
        raise SystemExit(f"refusing namespace {namespace!r}; only {ALLOWED_NAMESPACE} is allowed")
    result = subprocess.run(
        [
            "kubectl",
            "get",
            "pods",
            "-n",
            namespace,
            "-l",
            LABEL,
            "--field-selector=status.phase=Running",
            "-o",
            "jsonpath={.items[*].metadata.name}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    names = [name for name in result.stdout.split() if name]
    return names


def delete_pod(namespace, name, execute):
    if namespace != ALLOWED_NAMESPACE:
        raise SystemExit(f"refusing namespace {namespace!r}; only {ALLOWED_NAMESPACE} is allowed")
    print(f"selected pod {namespace}/{name} label {LABEL}")
    if not execute:
        print("dry-run: no pod deleted. Pass --execute to delete.")
        return
    subprocess.run(
        ["kubectl", "delete", "pod", "-n", namespace, name, "--wait=false"],
        check=True,
    )
    print(f"deleted {namespace}/{name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=ALLOWED_NAMESPACE)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually delete one pod (default is dry-run)",
    )
    args = parser.parse_args(argv)
    names = list_pods(args.namespace)
    if not names:
        print(f"no Running pods in {args.namespace} with {LABEL}")
        return 1
    delete_pod(args.namespace, random.choice(names), args.execute)
    return 0


if __name__ == "__main__":
    sys.exit(main())
