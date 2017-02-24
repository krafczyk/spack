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
from llnl.util.filesystem import join_path
from llnl.util import tty
from spack.architecture import sys_type
from spack.package import InstallError
import os
from shutil import copy


class Enzo(Package):
    """The Enzo package provides the hydrodynamic code enzo"""

    homepage="http://enzo-project.org/"
    url="https://bitbucket.org/enzo/enzo-dev/get/enzo-2.5.tar.bz2"

    version("development", hg="https://bitbucket.org/enzo/enzo-dev")
    version("stable", hg="https://bitbucket.org/enzo/enzo-dev", revision='stable')
    version("2.5", "ede4a3a59cabf2cdb4a29c49f5bedb20")
    version("2.4", "ad296817307be83b3bc9fe9b0494df8a")
    version("2.3", "0b8a47117ef95fd561c3319e8992ddf9")
    version("2.2", "65fe5a8dced223753e02aaa9e3e92603")
    version("2.1.1", "0fe775d0a05d5e434b7d1c3e927146d2")
    version("2.1.0", "224a426312af03a573c2087b6d94a2d4")
    
    variant("mode", default='debug', values=('warn', 'debug', 'high', 'aggressive'),
            exclusive=True, validator=None)
    variant("cray", default=False, description="Use for compilation on cray computers")
    variant("bluewaters", default=False, description="Use for compilation on bluewaters")

    depends_on('python@:2.7.999', type=('build'))
    depends_on('mercurial', type=('build'))
    depends_on('makedepend', type=('build'))
    depends_on('hdf5@1.8.16', type=('build', 'link', 'run'))
    depends_on('mpi', type=('build', 'link', 'run'), when="~cray")

    def install(self, spec, prefix):
        build_option = ""
        if self.spec.satisfies('mode=warn'):
            build_option = 'opt-warn'
        elif self.spec.satisfies('mode=debug'):
            build_option = 'opt-debug'
        elif self.spec.satisfies('mode=high'):
            build_option = 'opt-high'
        elif self.spec.satisfies('mode=aggressive'):
            build_option = 'opt-aggressive'
        else:
            raise InstallError("mode wasn't found in spec (%s) !" % self.spec);

        # destroy old bin
        if os.path.exists("bin"):
            rmtree("bin")
        mkdir("bin")
        
        # First run configure
        configure()
            
        # First, build enzo
        cd("src/enzo")

        tty.msg("Current directory is: %s" % os.getcwd())        

        # Remove configuration file
        if(os.path.exists("Make.mach.spack")):
            remove("Make.mach.spack")

        #Write configuration file
        bcf = open("Make.mach.spack", "w")
        bcf.write("""
#=======================================================================\n
#\n
# FILE:        Make.mach.spack\n
#\n
# DESCRIPTION: Makefile settings for a machine using spack\n
#\n
# AUTHOR:      Matthew Krafczyk (krafczyk.matthew@gmail.com)\n
#\n
# DATE:        2017-02-09\n
#\n
# This configuration is built with w/e is needed using spack\n
#\n
#=======================================================================\n
\n
MACH_TEXT  = Spack on %s\n
MACH_VALID = 1\n
MACH_FILE  = Make.mach.spack\n
\n
#-----------------------------------------------------------------------\n
# Install paths (local variables)\n
#-----------------------------------------------------------------------\n
\n
""" % sys_type())

	if "+cray" in spec:
        	bcf.write("LOCAL_MPI_INSTALL = \n")
	else:
        	mpi_prefix = spec['mpi'].prefix
        	bcf.write("LOCAL_MPI_INSTALL = %s\n" % mpi_prefix)
        hdf5_prefix = spec['hdf5'].prefix
        bcf.write("LOCAL_HDF5_INSTALL = %s\n" % hdf5_prefix)
	python_prefix = spec['python'].prefix
	bcf.write("LOCAL_PYTHON_INSTALL = %s\n" % python_prefix)

        bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Compiler settings\n
#-----------------------------------------------------------------------\n
\n
MACH_CPP       = cpp # C preprocessor command\n
\n
# With MPI\n
\n""")

	if "+cray" in spec:
		bcf.write("MACH_CC_MPI = cc\n")
		bcf.write("MACH_CXX_MPI = CC\n")
		bcf.write("MACH_FC_MPI = ftn\n")
		bcf.write("MACH_F90_MPI = ftn\n")
		bcf.write("MACH_LD_MPI = CC\n")
		bcf.write("\n")
		bcf.write("# Without MPI\n")
		bcf.write("\n")
		bcf.write("MACH_CC_NOMPI = cc\n")
		bcf.write("MACH_CXX_NOMPI = CC\n")
		bcf.write("MACH_FC_NOMPI = ftn\n")
		bcf.write("MACH_F90_NOMPI = ftn\n")
		bcf.write("MACH_LD_NOMPI = CC\n")
	else:
		bcf.write("MACH_CC_MPI = mpicc\n")
		bcf.write("MACH_CXX_MPI = mpic++\n")
		bcf.write("MACH_FC_MPI = gfortran\n")
		bcf.write("MACH_F90_MPI = gfortran\n")
		bcf.write("MACH_LD_MPI = mpic++\n")
		bcf.write("\n")
		bcf.write("# Without MPI\n")
		bcf.write("\n")
		bcf.write("MACH_CC_NOMPI = gcc\n")
		bcf.write("MACH_CXX_NOMPI = g++\n")
		bcf.write("MACH_FC_NOMPI = gfortran\n")
		bcf.write("MACH_F90_NOMPI = gfortran\n")
		bcf.write("MACH_LD_NOMPI = g++\n")

	bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Machine-dependent defines\n
#-----------------------------------------------------------------------\n
\n""")

	if "+cray" in spec:
		bcf.write("MACH_DEFINES = -DNO_IO_LOG"
		          " -DSYSCALL -DH5_USE_16_API "
		          "-DLINUX\n")
	else:
		bcf.write("MACH_DEFINES = -DLINUX "
		          "-DH5_USE_16_API\n")

	bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Compiler flag settings\n
#-----------------------------------------------------------------------\n
\n
\n
MACH_CPPFLAGS = -P -traditional \n
MACH_CFLAGS   = \n""")

        tty.msg("spec.dependencies: {}".format(type(spec.dependencies())))
	#if 'mpich' in spec.dependencies():
	#	bcf.write("MACH_CXXFLAGS = "
	#	          "-DMPICH_IGNORE_CXX_SEEK "
	#	          "-DMPICH_SKIP_MPICXX\n")
	#else:
	#	bcf.write("MACH_CXXFLAGS = \n")
	bcf.write("MACH_CXXFLAGS = \n")
	
	if '+cray' in spec:
		bcf.write("MACH_FFLAGS = "
		          "-fno-second-underscore "
		          "-ffixed-line-length-132 "
		          "-m64\n")
		bcf.write("MACH_F90FLAGS = "
		          "-fno-second-underscore "
		          "-m64\n")
		bcf.write("MACH_LDFLAGS = -Bdynamic\n")
	else:
		bcf.write("MACH_FFLAGS = "
		          "-fno-second-underscore "
		          "-ffixed-line-length-132\n")
		bcf.write("MACH_F90FLAGS = "
		          "-fno-second-underscore\n")
		bcf.write("MACH_LDFLAGS = \n")
	bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Optimization flags\n
#-----------------------------------------------------------------------\n
\n""")

	bcf.write("MACH_OPT_WARN        = -Wall\n")
	bcf.write("MACH_OPT_DEBUG        = -g\n")
	if "+bluewaters" in spec:
		bcf.write("MACH_OPT_HIGH = -O2 "
		          "-finline-functions -fwhole-program "
		          "-flto -march=bdver1 -mtune=bdver1 "
		          "-mprefer-avx128 -ftree-vectorize\n")
	else:
		bcf.write("MACH_OPT_HIGH = -O2\n")
	bcf.write("MACH_OPT_AGGRESSIVE = -O3\n")
	bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Includes\n
#-----------------------------------------------------------------------\n
\n""")
	if "+cray" in spec:
		bcf.write("LOCAL_INCLUDES_MPI = \n")
	else:
		bcf.write("LOCAL_INCLUDES_MPI = -I$(LOCAL_MPI_INSTALL)/include\n")
	bcf.write("LOCAL_INCLUDES_HDF5 = -I$(LOCAL_HDF5_INSTALL)/include\n")
	bcf.write("LOCAL_INCLUDES_HYPRE = \n")
	bcf.write("\n")
	bcf.write("MACH_INCLUDES = $(LOCAL_INCLUDES_MPI) $(LOCAL_INCLUDES_HDF5)\n")
	bcf.write("MACH_INCLUDES_MPI = $(LOCAL_INCLUDES_MPI)\n")
	bcf.write("""
\n
#-----------------------------------------------------------------------\n
# Libraries\n
#-----------------------------------------------------------------------\n
\n""")

	if "+cray" in spec:
		bcf.write("LOCAL_LIBS_MPI = \n")
	else:
		bcf.write("LOCAL_LIBS_MPI = -L$(LOCAL_MPI_INSTALL)/lib "
			  "-lmpi -lmpicxx\n")
	bcf.write("LOCAL_LIBS_HDF5 = -L$(LOCAL_HDF5_INSTALL)/lib "
		  "-lhdf5 -lz\n")
	bcf.write("\n")
	if "+cray" in spec:
		bcf.write("LOCAL_LIBS_MACH = \n")
	else:
		bcf.write("LOCAL_LIBS_MACH = -lgfortran\n")
	bcf.write("""
\n
MACH_LIBS         = $(LOCAL_LIBS_HDF5) $(LOCAL_LIBS_MACH)\n
MACH_LIBS_MPI     = $(LOCAL_LIBS_MPI)\n""")
        bcf.close()

        # Set machine options
        make("machine-spack")
        # Set debug mode
        make(build_option)
        make("clean")
        # Build
        make()

        # Now for the inits tool
        cd("../inits")
        make("machine-spack")
        make("clean")
        make(build_option)
        make()

        # And the ring tool
        cd("../ring")
        make("machine-spack")
        make(build_option)
        make("clean")
        make()
        copy('ring.exe', '../../bin/ring')

        cd("../..")
        # Install results
        mkdirp(join_path(prefix, "bin"))
        for item in os.listdir("bin"):
            install("bin/%s" % item, join_path(prefix, "bin/%s" % item))
