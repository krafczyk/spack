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
import copy

import llnl.util.tty as tty

import spack.config
from spack.util.decorators import static_vars
from spack.native.packages import PackageManager, replace_vars
from spack.util.executable import Executable

class Arch64PackageManager(PackageManager):
    pacman = Executable("pacman")
    archname = 'arch64'

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

    def install(self, spec):
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
