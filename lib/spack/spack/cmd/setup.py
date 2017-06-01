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
from __future__ import print_function
import spack
import spack.store
import spack.package
import spack.cmd
import spack.cmd.install as install
import spack.cmd.common.arguments as arguments
from llnl.util.filesystem import set_executable
from spack import which
from spack.stage import DIYStage

description = "create a configuration script and module, but don't build"
section = "developer"
level = "long"


def setup_parser(subparser):
    subparser.add_argument(
        '-i', '--ignore-dependencies', action='store_true', dest='ignore_deps',
        help="do not try to install dependencies of requested packages")
    subparser.add_argument(
        '-v', '--verbose', action='store_true', dest='verbose',
        help="display verbose build output while installing")
    subparser.add_argument(
        'spec', nargs=argparse.REMAINDER,
        help="specs to use for install. must contain package AND version")

    cd_group = subparser.add_mutually_exclusive_group()
    arguments.add_common_arguments(cd_group, ['clean', 'dirty'])


def spack_transitive_include_path():
    return ';'.join(
        os.path.join(dep, 'include')
        for dep in os.environ['SPACK_DEPENDENCIES'].split(os.pathsep)
    )


def write_spconfig(package):
    # Set-up the environment
    spack.build_environment.setup_package(package)

    cmd = [str(which('cmake'))] + package.std_cmake_args + package.cmake_args()

    env = dict()


def get_spconfig_fname(package):
    return 'spconfig.py'


def setup(self, args):
    kwargs = install.validate_args(args)

    # Spec from cli
    spec = spack.cmd.parse_specs(
        args.package, concretize=True, allow_multi=False)
    install.show_spec(spec, args)

    with install.setup_logging(spec, args):
        install.top_install(
            spec, setup=set([spec.name]),
            spconfig_fname_fn=get_spconfig_fname,
            **kwargs)
