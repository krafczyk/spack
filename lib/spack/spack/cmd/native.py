##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
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
from spack.external_adapters import get_available_package_managers, get_package_manager

description = "query native system packages "
section = "developer"
level = "long"

def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='native_command')

    list_avail_parser = sp.add_parser('list_available', help='list available native package managers spack finds')
    
    list_parser = sp.add_parser('list', help='list native packages spack finds')
    list_parser.add_argument('manager', type=str, help="package manager to list from")
    list_parser.add_argument('search', type=str, nargs='?', default=None,
                             help="search for a specific package")

    install_parser = sp.add_parser('install', help='install a native package')
    install_parser.add_argument('manager', type=str, help="package manager to list from")
    install_parser.add_argument('spec', type=str,
                                help="spec to attempt to install")

def native_list_avail(args):
    managers = get_available_package_managers()
    for man_name in managers:
        print(man_name)
    
def native_list(args):
    try:
        manager = get_package_manager(args.manager)
    except:
        tty.error("%s is not available." % args.manager)
        return

    found = manager.list(search_item = args.search)
    for item in found:
        print("%s@%s" % (item[0], item[1]))
    tty.info("Found %i packages" % len(found))

def native_install(args):
    try:
        manager = get_package_manager(args.manager)
    except:
        tty.error("%s is not available." % args.manager)

    manager.install(args.spec)

def native(self, args):
    action = {'list_available': native_list_avail,
              'list': native_list,
              'install': native_install}
    action[args.native_command](args)
