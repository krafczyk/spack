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
import llnl.util.tty as tty
import spack
import spack.cmd
import spack.cmd.common.arguments as arguments

description = "Bootstrap packages needed for spack to run smoothly"


def setup_parser(subparser):
    subparser.add_argument(
        '-j', '--jobs', action='store', type=int,
        help="explicitly set number of make jobs. default is #cpus")
    subparser.add_argument(
        '--keep-prefix', action='store_true', dest='keep_prefix',
        help="don't remove the install prefix if installation fails")
    subparser.add_argument(
        '--keep-stage', action='store_true', dest='keep_stage',
        help="don't remove the build stage if installation succeeds")
    subparser.add_argument(
        '-n', '--no-checksum', action='store_true', dest='no_checksum',
        help="do not check packages against checksum")
    subparser.add_argument(
        '-v', '--verbose', action='store_true', dest='verbose',
        help="display verbose build output while installing")

    cd_group = subparser.add_mutually_exclusive_group()
    arguments.add_common_arguments(cd_group, ['clean', 'dirty'])

    subparser.add_argument(
        '--run-tests', action='store_true', dest='run_tests',
        help="run package level tests during installation"
    )


def bootstrap(parser, args, **kwargs):
    kwargs.update({
        'keep_prefix': args.keep_prefix,
        'keep_stage': args.keep_stage,
        'install_deps': 'dependencies',
        'make_jobs': args.jobs,
        'run_tests': args.run_tests,
        'verbose': args.verbose,
        'dirty': args.dirty
    })

    # Define list of specs which need to be installed
    needed_specs = ['environment-modules~X']

    for needed_spec in needed_specs:
        tty.msg("Need %s" % needed_spec)
        installed_specs = spack.store.db.query(needed_spec)
        if(len(installed_specs) == 0):
            possible_specs = spack.cmd.parse_specs(needed_spec,
                                                   concretize=True)
            spec = possible_specs[0]
            tty.msg("Installing %s to satisfy need for %s" %
                    (spec, needed_spec))
            kwargs['explicit'] = True
            package = spack.repo.get(spec)
            package.do_install(**kwargs)
        else:
            tty.msg("%s Already Installed" % needed_spec)
