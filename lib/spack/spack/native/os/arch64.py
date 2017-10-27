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

from spack.util.decorators import static_vars
from spack.native.packages import PackageManager
from spack.util.executable import Executable

class Arch64PackageManager(PackageManager):
    pacman = Executable("pacman")

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
                    
        tty.info("Found %i packages" % len(found))
        for item in found:
            print("%s@%s" % (item[0], item[1]))


@static_vars(manager=None)
def fetch_manager():
    if fetch_manager.manager is None:
        manager = Arch64PackageManager()
    return manager
