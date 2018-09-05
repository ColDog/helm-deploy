import delete
import apply
import optparse

usage = "usage: helm-deploy (apply|delete) [options] name chart"
parser = optparse.OptionParser(usage)
parser.add_option("-c", "--context", dest="context", help="Kubernetes context")
parser.add_option("-u", "--as", dest="as_user", help="Kubernetes user")
parser.add_option("-g", "--as-group", dest="as_group", help="Kubernetes user")
parser.add_option("-n", "--namespace", dest="namespace", help="Kubernetes namespace")

(options, args) = parser.parse_args()
options = vars(options)

if len(args) != 3:
    parser.error("incorrect number of arguments")

arg = args[0]
name = args[1]
chart = args[2]


if arg == "delete":
    delete.command(options, name, chart)
elif arg == "apply":
    apply.command(options, name, chart)
else:
    parser.error(f"unkown command {arg}")
