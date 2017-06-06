##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
import sys
import os
import argparse

import llnl.util.tty as tty

import spack
import spack.cmd
import spack.cmd.common.arguments as arguments
from spack.stage import DIYStage

description = "do-it-yourself: build from an existing source directory"
section = "developer"
level = "long"


def setup_parser(subparser):
    subparser.add_argument(
        '-j', '--jobs', action='store', type=int,
        help="explicitly set number of make jobs. default is #cpus")
    subparser.add_argument(
        '-i', '--ignore-dependencies', action='store_true', dest='ignore_deps',
        help="don't try to install dependencies of requested packages")
    subparser.add_argument(
        '--keep-prefix', action='store_true',
        help="do not remove the install prefix if installation fails")
    subparser.add_argument(
        '--skip-patch', action='store_true',
        help="skip patching for the DIY build")
    subparser.add_argument(
        '-q', '--quiet', action='store_true', dest='quiet',
        help="do not display verbose build output while installing")
    subparser.add_argument(
        '-d', '--source-dir',
        help="Indicate the directory to find the package's source code")
    subparser.add_argument(
        'spec', nargs=argparse.REMAINDER,
        help="specs to use for install. must contain package AND version")

    cd_group = subparser.add_mutually_exclusive_group()
    arguments.add_common_arguments(cd_group, ['clean', 'dirty'])


def diy(self, args, **kwargs):
    if not args.spec:
        tty.die("spack diy requires a package spec argument.")

    if args.jobs is not None:
        if args.jobs <= 0:
            tty.die("The -j option must be a positive integer!")

    specs = spack.cmd.parse_specs(args.spec)
    if len(specs) > 1:
        tty.die("spack diy only takes one spec.")

    spec = specs[0]
    if not spack.repo.exists(spec.name):
        tty.die("No package for '{0}' was found.".format(spec.name),
                "  Use `spack create` to create a new package")

    if not spec.versions.concrete:
        tty.die(
            "spack diy spec must have a single, concrete version. "
            "Did you forget a package version number?")

    spec.concretize()
    package = spack.repo.get(spec)

    if package.installed:
        tty.error("Already installed in %s" % package.prefix)
        tty.msg("Uninstall or try adding a version suffix for this DIY build.")
        sys.exit(1)

    source_path = args.source_dir
    if source_path is None:
        source_path = os.getcwd()
    source_path = os.path.abspath(source_path)

    package.stage = DIYStage(source_path)

    # TODO: make this an argument, not a global.
    spack.do_checksum = False

    kwargs.update({
        'keep_prefix': args.keep_prefix,
        'install_deps': not args.ignore_deps,
        'verbose': not args.quiet,
        'keep_stage': True,
        'dirty': args.dirty
    })
    
    if args.jobs is not None:
        kwargs.update({
            'make_jobs': args.jobs,
        })

    package.do_install(**kwargs)
