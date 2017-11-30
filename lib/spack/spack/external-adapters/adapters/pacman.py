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
from spack.native.packages import PackageManager
from spack.util.executable import Executable

class Pacman(PackageManager):
    pacman = Executable("pacman")
    archname = 'arch64'

    @classmethod
    def available(cls):
        pass

    def list(self, search_item=None):
        pacman_output = self.pacman('-Q', output=str)
        lines = pacman_output.split("\n")
        found = []
        for line in lines:
            line_items = line.split(' ')
            if len(line_items) == 2:
                add = False
                if search_item and re.search(search_item, line_items[0]):
                    add = True
                elif search_item is None:
                    add = True
                if add:
                    found.append([line_items[0], line_items[1]])
                    
        return found
        tty.info("Found %i packages" % len(found))
        for item in found:
            print("%s@%s" % (item[0], item[1]))

    def file_list(self, package_name):
        com_output = self.pacman('-Ql', package_name, output=str)
        lines = com_output.split("\n")
        files = []
        for line in lines:
            if line != "":
                file_path = re.sub("^%s " % package_name, "", line)
                files.append(file_path)
        return files

    def file_map(self, filepath):
        return re.sub("^/usr/", "", filepath)

@static_vars(manager=None)
def fetch_manager():
    if fetch_manager.manager is None:
        manager = Arch64PackageManager()
    return manager
