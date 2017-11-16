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
import re
import copy

import llnl.util.tty as tty

import spack

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

    def install(self, spec):
        "Find and install the nearest native package which staisfies the spec."
        # Get and concretize spec from command line
        specs = spack.cmd.parse_specs(spec, concretize=True)
        spec = specs[0]

        # We need to find a matching package in the system repo
        system_package_name = None

        # Find whether there is plain rule for this package
        try:
            rules_list = spack.config.get_config("packman")[self.archname][spec.name]
            for rule in rules_list:
                # Find whether a rule matches this spec.
                rule_spec = spack.cmd.parse_specs(rule['spec'])[0]
                if spec.satisfies(rule_spec):
                    system_package_name = rule['package']
        except KeyError:
            pass

        if system_package_name is None:
            # Check regex matching list
            regex_list = spack.config.get_config("packman")[self.archname]['regex-matching-list']

            for regex_item in regex_list:
                match =  re.match("^%s$" % (regex_item['name']), spec.name)
                if match:
                    package = match.group(0)
                    matched = match.group(1)
                    for shim in regex_item['shims']:
                        shim_spec_pattern = copy.copy(shim['spec'])
                        shim_spec = replace_vars(shim_spec_pattern, package, matched)
                        if spec.satisfies(shim_spec):
                            shim_package_pattern = copy.copy(shim['package'])
                            system_package_name = replace_vars(shim_package_pattern, package, matched)
                            break
                    if system_package_name:
                        break

        if system_package_name is None:
            tty.die("There was no appropriate plain rule nor regex rule for the package %s." % spec.name)

        # Check if system package exists
        system_package_list = self.list()
        matches = []
        for system_package in system_package_list:
            match = re.match("^%s$" % system_package_name, system_package[0])
            if match:
                matches.append([match.group(0), system_package[1]])

        if len(matches) == 0:
            tty.die("Couldn't find any matching system packages which matched the pattern %s!" % shim_rule['pattern'])

        if len(matches) > 1:
            message = "Too many packages match the pattern %s! They were: "
            for match in matches:
                message += "%s " % match[0]
            tty.die(message)

        # We have one package which matches now
        tty.info("%s@%s satisfies %s" % (system_package_name, matches[0][1], spec))
        tty.info("This package contains the following files:")
        files = self.file_list(system_package_name)
        print(files)
        tty.info("The mapping will be:")
        file_mapping = self.apply_map(files)
        for mapping in file_mapping:
            print("%s -> ${PREFIX}/%s" % (mapping[0], mapping[1]))


    def list(self, search_item=None):
        "Query the system package manager for a list of installed pacakges"
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
