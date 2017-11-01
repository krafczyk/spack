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
from spack import *


class Glibc(AutotoolsPackage):
    """The GNU C Library"""

    homepage = "https://www.gnu.org/software/libc/"
    url      = "https://ftp.gnu.org/gnu/libc/glibc-2.26.tar.gz"

    version('2.26', 'ae2a3cddba005b34792dabe8c103e866')
    version('2.25', '0c9f827298841dbf3bff3060f3d7f19c')
    version('2.24', 'f0017697aeadf0d7cc127a9f52852480')
    
    # Need GCC 4.9 or newer
    conflicts('%gcc@:4.8')

    ##For glibc 2.26?
    #depends_on('make@3.79')
    #depends_on('binutils@2.25:')
    #depends_on('texinfo@4.7:')
    #depends_on('awk@3.1.2:')
    #depends_on('perl')
    #depends_on('sed@3.02:')
    ##depends_on('autoconf@2.69')
    ##depends_on('gettext@0.10.36:')
    ##depends_on('bison@2.7:')

    build_directory = 'spack-build'

    def configure_args(self):
        # Possible future stuff: kernel dependencies??
        args = []
        return args
