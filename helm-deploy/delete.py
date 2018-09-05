import yaml
import kubernetes


def command(options, name, chart):
    namespace = options.get("namespace") or "default"

    kubectl = kubernetes.get_kubectl(
        as_user=options.get("as_user"),
        as_group=options.get("as_group"),
        context=options.get("context"),
        namespace=namespace,
    )

    def remove(manifest):
        try:
            kubectl("delete", manifest["kind"], manifest["metadata"]["name"])
        except Exception as e:
            pass

    def run(data):
        for manifest in yaml.load_all(data):
            if not manifest:
                continue
            if not kubernetes.is_task(manifest):
                remove(manifest)

    print(f"current context:", kubectl("config", "current-context", capture=True))
    print(f"deleting chart: {chart}, name: {name}, namespace: {namespace}")

    chart = kubernetes.render_chart(chart, name, namespace)
    run(chart)
