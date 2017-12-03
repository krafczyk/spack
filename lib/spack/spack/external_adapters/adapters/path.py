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
import os

import llnl.util.tty as tty

import spack.config
from spack.util.decorators import static_vars
from spack.external_adapters.package_manager import PackageManager
from spack.util.executable import Executable, which

class Path(PackageManager):
    @classmethod
    def available(cls):
        return True

    @classmethod
    def manager_name(cls):
        return "path"

    def __init__(self):
        print("Path Init called!")

    def list(self, search_item=None):
        return []

    def file_list(self, package_name):
        files = []
        return files

    def file_map(self, package_name, filepath):
        full_path = os.path.abspath(package_name)
        return re.sub("^{}".format(full_path), "", filepath)

#@static_vars(manager=None)
#def fetch_manager():
#    if fetch_manager.manager is None:
#        manager = Path()
#    return manager
