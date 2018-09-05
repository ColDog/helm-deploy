import yaml
import kubernetes
import plugins.istio
import output
import sys
import time


def command(options, name, chart):
    namespace = options.get("namespace") or "default"

    kubectl = kubernetes.get_kubectl(
        as_user=options.get("as_user"),
        as_group=options.get("as_group"),
        context=options.get("context"),
        namespace=namespace,
    )

    def apply_manifest(manifest):
        rendered = yaml.dump(manifest)
        kubectl("apply", "-f", "-", write=rendered, capture=True)

    def wait_for_rollout(manifest):
        kind = manifest["kind"]
        name = manifest["metadata"]["name"]
        output.write(f"waiting for {kind}/{name} to rollout")
        kubectl("rollout", "status", kind, name)

    def apply_task(manifest):
        name = manifest["metadata"]["name"]
        kind = manifest["kind"]
        output.write(f"running task {kind}/{name}")
        rendered = yaml.dump(manifest)

        try:
            kubectl("apply", "-f", "-", write=rendered)
            kubernetes.await_pod(kubectl, name)
        finally:
            kubectl("delete", "pods", name, quiet=True)

    def run(manifests):
        for manifest in manifests:
            t1 = time.time()
            output.write(
                f"Deploying {manifest['kind']} / {manifest['metadata']['name']}"
            )

            if not manifest:
                continue
            if kubernetes.is_task(manifest):
                apply_task(manifest)
            else:
                if kubernetes.is_istio_enabled(manifest):
                    manifest = plugins.istio.inject(manifest)

                apply_manifest(manifest)
                if manifest["kind"] == "Deployment":
                    wait_for_rollout(manifest)

            elapsed = time.strftime("%S", time.gmtime(time.time() - t1))
            output.write(f"Deployment complete ({elapsed}s)\n", fg="purple")

    context = kubectl("config", "current-context", capture=True).decode().strip()

    output.write("=== Initializing Deploy ===\n", fg="green")
    output.write(f"Chart:     {chart}")
    output.write(f"Name:      {name}")
    output.write(f"Namespace: {namespace}")
    output.write(f"Context:   {context}")

    chart = kubernetes.render_chart(chart, name, namespace)
    manifests = list(yaml.load_all(chart))

    output.write("\nDiscovering types:")
    for manifest in manifests:
        output.write(f"- {manifest['kind']} / {manifest['metadata']['name']}")

    output.write("\n=== Starting Deploy ===\n", fg="green")

    try:
        run(manifests)
    except Exception as e:
        output.write(f"Deploy failed: {str(e)}", fg="red")
        sys.exit(1)
