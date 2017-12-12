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
import spack.store
import spack.hooks
import spack.store
from spack.util.decorators import memoize_class

def replace_vars(in_string, package, match):
    in_string = in_string.replace('${PACKAGE}', package)
    in_string = in_string.replace('${MATCH}', match)
    return in_string

class PackageManager(object):
    """ The Manager class is a high level interface with a native package
        manager.
    """

    @classmethod
    def available(cls):
        return False

    @classmethod
    def manager_name(cls):
        return "none"

    def __init__(self, *args):
        print("PackageManager Init called!")

    def path(self, spec):
        return None

    def load(self, spec):
        print("Not Defined!")

    def check_package_exists(self, package_name):
        # Check if package exists in manager
        package_list = self.list()
        matches = []
        for package in package_list:
            match = re.match("^%s$" % package_name, package[0])
            if match:
                matches.append([match.group(0), package[1]])

        if len(matches) == 0:
            tty.error("Couldn't find any matching system packages which matched the pattern %s!" % shim_rule['pattern'])
            return False

        if len(matches) > 1:
            message = "Too many packages match the pattern %s! They were: "
            for match in matches:
                message += "%s " % match[0]
            tty.error(message)
            return False
        return True

    def get_package_translation_rules(self, spec):
        rule_candidates = []
        try:
            rules_list = spack.config.get_config("packman")[self.manager_name()][spec.name]
            for rule in rules_list:
                # Find whether a rule matches this spec.
                rule_spec = spack.cmd.parse_specs(rule['spec'])[0]
                if spec.satisfies(rule_spec):
                    try:
                        version_demangle = rule['version-demangle']
                    except KeyError:
                        version_demangle = ''
                    rule_candidates.append([rule['package'],version_demangle])
        except KeyError:
            pass

        if len(rule_candidates) == 0:
            # Check regex matching list
            regex_list = spack.config.get_config("packman")[self.manager_name()]['regex-matching-list']

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
                            try:
                                version_demangle = rule['version-demangle']
                            except KeyError:
                                version_demangle = ''
                            rule_candidates.append([replace_vars(shim_package_pattern, package, matched),version_demangle])

        if len(rule_candidates) == 0:
            # Pass out a plain rule. i.e. same name as spack package, no version translation
            rule_candidates.append([spec.name, ''])
        if len(rule_candidates) > 1:
            message = "There were multiple matching plain rules or regex rules for the package %s.\n" % spec.name
            message += "They were:\n"
            for rule in rule_candidates:
                message += "    %s\n" % rule
            tty.die(message)
        return rule_candidates

    def check_package_name(self, spec, package_name):
        rule_candidates = self.get_package_translation_rules(spec)
        if package_name == rule_candidates[0]:
            return True
        else:
            return False

    @memoize_class
    def get_package_info(self, spec):
        # Expect a spec object

        # We need to find a matching package in the external repo
        [ package_name, version_demangle] = self.get_package_translation_rules(spec)[0]
        package_list = self.list()
        for package_info in package_list:
            if package_name == package_info[0]:
                package_version = None
                if version_demangle != "":
                    match = re.match(version_demangle, package_info[1])
                    if match:
                        package_version = match.group(1)
                    else:
                        tty.warn("Problem using version extraction! falling back to full version")
                if package_version is None:
                    package_version = package_info[1]
                return [ package_name, package_version ]
        return None

    def install_imp(self, spec, **kwargs):
        print("Not Implemented yet!!")
        pass

    def install(self, spec, **kwargs):
        "Find and install the specified external package."
        # Expect a concretized spec

        if not self.check_package_exists(spec.external_package):
            tty.die("Couldn't find a single package to install!")

        self.install_imp(spec, **kwargs)

    def uninstall(self, spec):
        print("Not Implemented yet!!")

    def list(self, search_item=None):
        "Query the system package manager for a list of installed packages"
        pass

    def file_list(self, package_name):
        "Get list of files associated with an installed system package"
        pass

    def apply_map(self, package_name, filelist):
        "Apply mapping heuristics returning a list mapping the system file path to the final prefix path"
        mapping = []
        for item in filelist:
            map_result = self.file_map(package_name, item)
            if map_result is not '':
                # Don't include plain directories
                if not os.path.isdir(item):
                    mapping.append([item, map_result])
        return mapping

    def file_map(self, package_name, filepath):
        "Heuristic map between installed file paths and final prefix path"
        pass


class FileCopyPackageManager(PackageManager):
    @classmethod
    def available(cls):
        return False

    @classmethod
    def manager_name(cls):
        return "file-copy"

    def __init__(self, *args):
        print("FileCopyPackageManager Init called!")

    def uninstall(self, spec):
        msg = 'Deleting package prefix [{0}]'
        tty.debug(msg.format(spec.short_spec))
        spack.store.layout.remove_install_directory(spec)

    def load(self, spec):
        pass

    def install_imp(self, spec, **kwargs):
        # Ensure package is not already installed
        layout = spack.store.layout

        # Create the install prefix
        if not os.path.exists(spec.prefix):
            layout.create_install_directory(spec)

        # Get file list
        package_name = spec.external_package
        files = self.file_list(package_name)
        #print(files)
        #tty.info("The mapping will be:")
        #Symbolically link files to destination
        file_mapping = self.apply_map(package_name, files)
        for mapping in file_mapping:
            file_path = '/'.join([spec.prefix, mapping[1]])
            file_dir = os.path.dirname(file_path)
            try:
                os.makedirs(file_dir)
            except:
                pass
            os.symlink(mapping[0], file_path)

        message = '{s.name}@{s.version} : generating module file'
        tty.msg(message.format(s=spec))
        spack.hooks.post_install(spec)
        
        message = '{s.name}@{s.version} : registering into DB'
        tty.msg(message.format(s=spec))
        # Add to DB
        spack.store.db.add(
            spec, layout, explicit=kwargs.get('explicit', False)
        )


class ModulePackageManager(PackageManager):
    @classmethod
    def available(cls):
        return False

    @classmethod
    def manager_name(cls):
        return "file-copy"

    def __init__(self, *args):
        print("FileCopyPackageManager Init called!")

    def uninstall(self, spec):
        pass

    def load(self, spec):
        print("Needs to be defined!!")
        #need to define load_module
        #load_module(spec.external_package)

    def install_imp(self, spec, **kwargs):
        message = '{s.name}@{s.version} : generating module file'
        tty.msg(message.format(s=spec))
        spack.hooks.post_install(spec)
        
        # Add to DB
        message = '{s.name}@{s.version} : registering into DB'
        tty.msg(message.format(s=spec))
        spack.store.db.add(
            spec, None, explicit=kwargs.get('explicit', False)
        )
