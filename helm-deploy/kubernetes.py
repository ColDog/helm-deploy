import sh
import time


def kubectl(
    *cmd,
    as_user=None,
    as_group=None,
    namespace=None,
    context=None,
    quiet=False,
    capture=False,
    write=None,
    verbose=False,
):
    args = []
    if context:
        args.append(f"--context={context}")
    if namespace:
        args.append(f"--namespace={namespace}")
    if as_user:
        args.append(f"--as={as_user}")
    if as_group:
        args.append(f"--as-group={as_group}")
    args.extend(cmd)
    return sh.sh(
        "kubectl",
        *args,
        quiet=quiet,
        capture=capture,
        write=write.encode() if write else None,
        verbose=verbose,
    )


def get_kubectl(as_user=None, as_group=None, namespace=None, context=None):
    def wrapped(*args, **kwargs):
        kwargs["as_user"] = as_user
        kwargs["as_group"] = as_group
        kwargs["context"] = context
        kwargs["namespace"] = namespace
        # kwargs["verbose"] = True
        return kubectl(*args, **kwargs)

    return wrapped


def pod_status(kubectl, name):
    status = kubectl("get", "pods", name, '-o=jsonpath="{.status.phase}"', capture=True)
    if not status:
        return None
    return status.decode("utf-8").replace('"', "")


def await_pod(kubectl, name):
    # Wait until the container is started.
    while True:
        status = pod_status(kubectl, name)
        if status != "ContainerCreating" and status != "Pending":
            break
        time.sleep(1)

    # Watch logs.
    kubectl("logs", "-f", name)

    # Await pod completion.
    while True:
        status = pod_status(kubectl, name)
        if status != "Running":
            break
        time.sleep(1)

    if status != "Succeeded":
        raise ValueError(f"Pod/{name} exited with status: {status}")


def render_chart(filename, name, namespace):
    return sh.sh(
        "helm",
        "template",
        "--name",
        name,
        "--namespace",
        namespace,
        filename,
        capture=True,
    ).decode()


def is_task(manifest):
    try:
        manifest["metadata"]["annotations"]["helm-deploy.k8s.io/task"]
        return True
    except KeyError:
        return False
    except TypeError:
        return False


def is_istio_enabled(manifest):
    try:
        manifest["metadata"]["annotations"]["helm-deploy.k8s.io/istio"]
        return True
    except KeyError:
        return False
    except TypeError:
        return False
