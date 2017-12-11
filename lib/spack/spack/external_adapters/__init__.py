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

import spack
import spack.external_adapters.adapters
from spack.util.decorators import static_vars
from spack.external_adapters.adapters import adapter_methods

@static_vars(manager_dict=None)
def get_available_package_managers():
    if get_available_package_managers.manager_dict is None:
        get_available_package_managers.manager_dict = {}
        for adapter_method in adapter_methods:
            manager_class = adapter_method[0]()
            if manager_class.available():
                get_available_package_managers.manager_dict[manager_class.manager_name()] = adapter_method[1]

    return get_available_package_managers.manager_dict

def get_package_manager(name):
    return get_available_package_managers()[name]()
