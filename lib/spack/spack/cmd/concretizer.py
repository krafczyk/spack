import sys
import os
import argparse

import llnl.util.tty as tty

import spack
import spack.cmd
import spack.cmd.common.arguments as arguments
import spack.spec
import spack.new_concretize

description = "testing new concretizer"
section = "developer"
level = "long"

def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='concretize_command')

    concretize_parser = sp.add_parser('concretize', help='concretize using the new concretizer')
    concretize_parser.add_argument('specs', help='specs to concretize', nargs="*")

def plain_concretize(args):
    specs = []
    for spec in args.specs:
        new_spec = spack.spec.Spec(spec)
        specs.append(new_spec)
    concretizer = spack.new_concretize.Concretizer(specs)
    concretizer.show()

def concretizer(self, args):
    action = {'concretize': plain_concretize}
    action[args.concretize_command](args)
