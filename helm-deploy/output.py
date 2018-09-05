import colors
import sys


def write(*args, **kwargs):
    sys.stdout.write(colors.color(" ".join(args), **kwargs) + "\n")
