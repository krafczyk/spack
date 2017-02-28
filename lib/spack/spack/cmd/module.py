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
from __future__ import print_function

import collections
import os
import shutil
import sys

import spack.cmd

from llnl.util import filesystem, tty
from spack.cmd.common import arguments
from spack.modules import module_types
from spack.util.executable import which

description = "manipulate module files"

# Dictionary that will be populated with the list of sub-commands
# Each sub-command must be callable and accept 3 arguments :
# - mtype : the type of the module file
# - specs : the list of specs to be processed
# - args : namespace containing the parsed command line arguments
callbacks = {}


def subcommand(subparser_name):
    """Registers a function in the callbacks dictionary"""
    def decorator(callback):
        callbacks[subparser_name] = callback
        return callback
    return decorator


def setup_parser(subparser):
    sp = subparser.add_subparsers(metavar='SUBCOMMAND', dest='subparser_name')

    # spack module refresh
    refresh_parser = sp.add_parser('refresh', help='regenerate module files')
    refresh_parser.add_argument(
        '--delete-tree',
        help='delete the module file tree before refresh',
        action='store_true'
    )
    arguments.add_common_arguments(
        refresh_parser, ['constraint', 'module_type', 'yes_to_all']
    )

    # spack module find
    find_parser = sp.add_parser('find', help='find module files for packages')
    arguments.add_common_arguments(find_parser, ['constraint', 'module_type'])

    # spack module rm
    rm_parser = sp.add_parser('rm', help='remove module files')
    arguments.add_common_arguments(
        rm_parser, ['constraint', 'module_type', 'yes_to_all']
    )

    # spack module loads
    loads_parser = sp.add_parser(
        'loads',
        help='prompt the list of modules associated with a constraint'
    )
    loads_parser.add_argument(
        '--input-only', action='store_false', dest='shell',
        help='generate input for module command (instead of a shell script)'
    )
    loads_parser.add_argument(
        '-p', '--prefix', dest='prefix', default='',
        help='prepend to module names when issuing module load commands'
    )
    loads_parser.add_argument(
        '-x', '--exclude', dest='exclude', action='append', default=[],
        help="exclude package from output; may be specified multiple times"
    )
    arguments.add_common_arguments(
        loads_parser, ['constraint', 'module_type', 'recurse_dependencies']
    )


class MultipleMatches(Exception):
    pass


class NoMatch(Exception):
    pass


@subcommand('loads')
def loads(mtype, specs, args):
    """Prompt the list of modules associated with a list of specs"""

    # We need modulecmd since we need to inspect some module files.
    modulecmd = which('modulecmd', required=True)
    modulecmd.add_default_arg('python')

    # Get a comprehensive list of specs
    if args.recurse_dependencies:
        specs_from_user_constraint = specs[:]
        specs = []
        # FIXME : during module file creation nodes seem to be visited
        # FIXME : multiple times even if cover='nodes' is given. This
        # FIXME : work around permits to get a unique list of spec anyhow.
        # FIXME : (same problem as in spack/modules.py)
        seen = set()
        seen_add = seen.add
        for spec in specs_from_user_constraint:
            specs.extend(
                [item for item in spec.traverse(order='post', cover='nodes')
                 if not (item in seen or seen_add(item))]
            )

    module_cls = module_types[mtype]
    modules = [(spec, module_cls(spec).use_name)
               for spec in specs if os.path.exists(module_cls(spec).file_name)]

    module_load_commands = {
        'tcl': 'module load ',
        'lmod': 'module load ',
        'dotkit': 'dotkit use '
    }

    module_unload_commands = {
        'tcl': 'module unload ',
        'lmod': 'module unload ',
        'dotkit': 'dotkit unuse '
    }

    d = {
        'load_command': '' if not args.shell else module_load_commands[mtype],
        'unload_command': '' if not args.shell else module_unload_commands[mtype],
        'prefix': args.prefix
    }
    exclude_set = set(args.exclude)
    # We build the lines to print
    comment_template = '{comment}'
    module_load_template = '{exclude}{load_command}{prefix}{name}\n'
    module_unload_template = '{exclude}{unload_command}{prefix}{name}\n'
    for spec, mod in modules:
        d['exclude'] = '## ' if spec.name in exclude_set else ''
        d['comment'] = '' if not args.shell else '# {0}\n'.format(
            spec.format())
        # FIXME: This procedure is not a complete
        # module loading solution. It only goes one level deep.
        prompt_lines = comment_template.format(**d)
        # Inspect module for load commands
        primary_mod_text = modulecmd('show', mod, output=str, error=str).split()
        modules_to_load = []
        modules_to_unload = []
        for i, word in enumerate(primary_mod_text):
            if word == 'conflict':
                modules_to_unload.append(primary_mod_text[i+1])
            if word == 'load':
                modules_to_load.append(primary_mod_text[i+1])
        # Inspect loaded modules for conflict statements.
        for mod_lo in modules_to_load:
            mod_text = modulecmd('show', mod_lo, output=str, error=str).split()
            for i, word in enumerate(mod_text):
                if word == 'conflict':
                    modules_to_unload.append(mod_text[i+1])
        # unload modules
        for mod_unload in modules_to_unload:
            d['name'] = mod_unload
            prompt_lines += module_unload_template.format(**d)
        # load modules
        for mod_load in modules_to_load:
            d['name'] = mod_load
            prompt_lines += module_load_template.format(**d)
        # load actual module
        d['name'] = mod
        prompt_lines += module_load_template.format(**d)
        print(prompt_lines)


@subcommand('find')
def find(mtype, specs, args):
    """
    Look at all installed packages and see if the spec provided
    matches any.  If it does, check whether there is a module file
    of type <mtype> there, and print out the name that the user
    should type to use that package's module.
    """
    if len(specs) == 0:
        raise NoMatch()

    if len(specs) > 1:
        raise MultipleMatches()

    spec = specs.pop()
    mod = module_types[mtype](spec)
    if not os.path.isfile(mod.file_name):
        tty.die('No {0} module is installed for {1}'.format(mtype, spec))
    print(mod.use_name)


@subcommand('rm')
def rm(mtype, specs, args):
    """Deletes module files associated with items in specs"""
    module_cls = module_types[mtype]
    specs_with_modules = [
        spec for spec in specs if os.path.exists(module_cls(spec).file_name)]
    modules = [module_cls(spec) for spec in specs_with_modules]

    if not modules:
        tty.msg('No module file matches your query')
        raise SystemExit(1)

    # Ask for confirmation
    if not args.yes_to_all:
        tty.msg(
            'You are about to remove {0} module files the following specs:\n'
            .format(mtype))
        spack.cmd.display_specs(specs_with_modules, long=True)
        print('')
        answer = tty.get_yes_or_no('Do you want to proceed?')
        if not answer:
            tty.die('Will not remove any module files')

    # Remove the module files
    for s in modules:
        s.remove()


@subcommand('refresh')
def refresh(mtype, specs, args):
    """Regenerate module files for item in specs"""
    # Prompt a message to the user about what is going to change
    if not specs:
        tty.msg('No package matches your query')
        return

    if not args.yes_to_all:
        tty.msg(
            'You are about to regenerate {name} module files for:\n'
            .format(name=mtype))
        spack.cmd.display_specs(specs, long=True)
        print('')
        answer = tty.get_yes_or_no('Do you want to proceed?')
        if not answer:
            tty.die('Will not regenerate any module files')

    cls = module_types[mtype]

    # Detect name clashes
    writers = [cls(spec) for spec in specs
               if spack.repo.exists(spec.name)]  # skip unknown packages.
    file2writer = collections.defaultdict(list)
    for item in writers:
        file2writer[item.file_name].append(item)

    if len(file2writer) != len(writers):
        message = 'Name clashes detected in module files:\n'
        for filename, writer_list in file2writer.items():
            if len(writer_list) > 1:
                message += '\nfile: {0}\n'.format(filename)
                for x in writer_list:
                    message += 'spec: {0}\n'.format(x.spec.format(color=True))
        tty.error(message)
        tty.error('Operation aborted')
        raise SystemExit(1)

    # Proceed regenerating module files
    tty.msg('Regenerating {name} module files'.format(name=mtype))
    if os.path.isdir(cls.path) and args.delete_tree:
        shutil.rmtree(cls.path, ignore_errors=False)
    filesystem.mkdirp(cls.path)
    for x in writers:
        x.write(overwrite=True)


def module(parser, args):
    # Qualifiers to be used when querying the db for specs
    constraint_qualifiers = {
        'refresh': {
            'installed': True,
            'known': True
        },
    }
    query_args = constraint_qualifiers.get(args.subparser_name, {})
    specs = args.specs(**query_args)
    module_type = args.module_type
    constraint = args.constraint
    try:
        callbacks[args.subparser_name](module_type, specs, args)
    except MultipleMatches:
        message = ("the constraint '{query}' matches multiple packages, "
                   "and this is not allowed in this context")
        tty.error(message.format(query=constraint))
        for s in specs:
            sys.stderr.write(s.format(color=True) + '\n')
        raise SystemExit(1)
    except NoMatch:
        message = ("the constraint '{query}' matches no package, "
                   "and this is not allowed in this context")
        tty.die(message.format(query=constraint))
