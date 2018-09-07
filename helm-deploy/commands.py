import yaml
import output
import kubernetes
import time
import plugins.istio


def order(manifests):
    precedence = [
        # One off components.
        "Pod",
        "Job",
        # Networking components.
        "VirtualService",
        "Gateway",
        "Service",
        "Ingress",
        # Deployments.
        "DaemonSet",
        "Deployment",
    ]
    ordered = []

    for kind in precedence:
        for idx, manifest in enumerate(manifests):
            if manifest["kind"] == kind:
                del manifests[idx]
                ordered.append(manifest)
    return ordered + manifests


def apply(kubectl, manifests):
    def apply_manifest(manifest):
        rendered = yaml.dump(manifest)
        kubectl("apply", "-f", "-", write=rendered, capture=True)

    def wait_for_rollout(manifest):
        kind = manifest["kind"]
        name = manifest["metadata"]["name"]
        output.write(f"waiting for {name} deployment to rollout...", fg="grey")
        kubectl("rollout", "status", kind, name)

    def apply_task(manifest):
        name = manifest["metadata"]["name"]
        rendered = yaml.dump(manifest)

        try:
            kubectl("apply", "-f", "-", write=rendered)
            output.write(f"streaming output for {name} task...", fg="grey")
            kubernetes.await_pod(kubectl, name)
        finally:
            kubectl("delete", "pods", name, quiet=True)

    for manifest in manifests:
        t1 = time.time()

        if not manifest:
            continue

        output.write(
            f"== applying {manifest['kind']} / {manifest['metadata']['name']}",
            style="bold",
        )
        if kubernetes.is_task(manifest):
            apply_task(manifest)
        else:
            if kubernetes.is_istio_enabled(manifest):
                manifest = plugins.istio.inject(manifest)

            apply_manifest(manifest)
            if manifest["kind"] == "Deployment":
                wait_for_rollout(manifest)

        elapsed = time.strftime("%S", time.gmtime(time.time() - t1))
        output.write(f"apply complete ({elapsed}s)\n", fg="purple", style="bold")


def delete(kubectl, manifests):
    def remove(manifest):
        try:
            kubectl("delete", manifest["kind"], manifest["metadata"]["name"])
        except Exception as e:
            pass

    for manifest in manifests:
        if not manifest:
            continue

        output.write(f"deleting {manifest['kind']} / {manifest['metadata']['name']}")
        if not kubernetes.is_task(manifest):
            remove(manifest)
