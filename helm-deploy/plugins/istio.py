import sh
import yaml


def inject(manifest):
    rendered = yaml.dump(manifest)
    injected = sh.sh(
        "istioctl", "kube-inject", "-f", "-", write=rendered.encode(), capture=True
    )
    for manifest in yaml.load_all(injected):
        return manifest
