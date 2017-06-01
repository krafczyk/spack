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
from spack import *


class CrayMpi(AutotoolsPackage):
    """Cray MPI is a cray implemented version of the
       high performance and widely portable implementation of
       the Message Passing Interface (MPI) standard."""

    homepage = "unknown"
    url = "unknown"
    list_url = "unknown"

    provides('mpi@:3.0')

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('MPICC',  spack_cc)
        spack_env.set('MPICXX', spack_cxx)
        spack_env.set('MPIF77', spack_fc)
        spack_env.set('MPIF90', spack_fc)

    def setup_dependent_package(self, module, dep_spec):
        self.spec.mpicc = spack_cc
        self.spec.mpicxx = spack_cxx
        self.spec.mpifc = spack_fc
        self.spec.mpif77 = spack_f77
