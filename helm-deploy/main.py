import commands
import optparse
import output
import kubernetes
import yaml
import sys

usage = "usage: helm-deploy (apply|delete) [options] name chart"
parser = optparse.OptionParser(usage)
parser.add_option("-c", "--context", dest="context", help="Kubernetes context")
parser.add_option("-u", "--as", dest="as_user", help="Kubernetes user")
parser.add_option("-g", "--as-group", dest="as_group", help="Kubernetes user")
parser.add_option("-n", "--namespace", dest="namespace", help="Kubernetes namespace")
parser.add_option("-f", "--values", dest="values", help="Helm chart value file")

(options, args) = parser.parse_args()
options = vars(options)

if len(args) != 3:
    parser.error("incorrect number of arguments")

arg = args[0]
name = args[1]
chart = args[2]
namespace = options.get("namespace") or "default"
values = options.get("values")

if arg == "delete":
    command = commands.delete
elif arg == "apply":
    command = commands.apply
else:
    parser.error(f"unkown command {arg}")

kubectl = kubernetes.get_kubectl(
    as_user=options.get("as_user"),
    as_group=options.get("as_group"),
    context=options.get("context"),
    namespace=namespace,
)

context = kubectl("config", "current-context", capture=True).decode().strip()

output.write(f"=== Initializing {arg} ===\n", fg="green", style="bold")
output.write(f"Chart:     {chart}")
output.write(f"Name:      {name}")
output.write(f"Namespace: {namespace}")
output.write(f"Context:   {context}")

chart = kubernetes.render_chart(chart, name, namespace, values)
manifests = commands.order(list(yaml.load_all(chart)))

output.write("\nDiscovering types:")
for manifest in manifests:
    output.write(
        f"- {manifest['kind']} / {manifest['metadata']['name']} ({manifest['apiVersion']})"
    )

output.write(f"\n=== Starting {arg} ===\n", fg="green", style="bold")

try:
    command(kubectl, manifests)
except Exception as e:
    output.write(f"Delete failed: {str(e)}", fg="red", style="bold")
    sys.exit(1)
