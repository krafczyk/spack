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
import os

import llnl.util.tty as tty


def replace_vars(in_string, package, match):
    in_string = in_string.replace('${PACKAGE}', package)
    in_string = in_string.replace('${MATCH}', match)
    return in_string

class PackageManager(object):
    """ The Manager class is a high level interface with a native package
        manager.
    """

    def __init__(self, *args):
        pass

    def list(self, search_item=None):
        "Query the system package manager for a list of installed pacakges"
        pass

    def install(self, spec):
        "Find and install the nearest native package which staisfies the spec."
        pass

    def file_list(self, package_name):
        "Get list of files associated with an installed system package"
        pass

    def apply_map(self, filelist):
        "Apply mapping heuristics returning a list mapping the system file path to the final prefix path"
        mapping = []
        for item in filelist:
            map_result = self.file_map(item)
            if map_result is not '':
                # Don't include plain directories
                if not os.path.isdir(item):
                    mapping.append([item, map_result])
        return mapping

    def file_map(self, filepath):
        "Heuristic map between installed file paths and final prefix path"
        pass
