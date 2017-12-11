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
import re

import llnl.util.tty as tty

import spack.config
from spack.util.decorators import static_vars
from spack.external_adapters.package_manager import PackageManager
from spack.util.executable import Executable, which

class EnvModule(PackageManager):
    @classmethod
    def available(cls):
        return False

    @classmethod
    def manager_name(cls):
        return "envmod"

    def __init__(self):
        print("EnvModule Init called!")

    def list(self, search_item=None):
        return []

    def install_imp(self, spec):
        print("Not implemented yet!")
        pass

    def file_list(self, package_name):
        files = []
        return files

    def file_map(self, package_name, filepath):
        return re.sub("^/usr/", "", filepath)

def get_manager_class():
    return EnvModule

@static_vars(manager=None)
def fetch_manager():
    if fetch_manager.manager is None:
        fetch_manager.manager = Path()
    return fetch_manager.manager

manager_methods = [get_manager_class, fetch_manager]
