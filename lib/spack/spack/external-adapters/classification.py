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
import platform

from spack.native.os import arch64

class_manager_fetchers = { ('linux', 'arch', 'x86_64'): arch64.fetch_manager }

def detect_class():
    resulting_class = ['','','']
    platform_string = platform.platform()
    if 'Linux' in platform_string:
        resulting_class[0] = 'linux'

    if 'with-arch' in platform_string:
        resulting_class[1] = 'arch'

    if 'x86_64' in platform_string:
        resulting_class[2] = 'x86_64'

    return tuple(resulting_class)
