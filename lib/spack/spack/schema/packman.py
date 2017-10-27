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
"""Schema for packman.yaml configuration files.

.. literalinclude:: ../spack/schema/packman.py
   :lines: 32-
"""


schema = {
    '$schema': 'http://json-schema.org/schema#',
    'title': 'Spack package manager shim file schema',
    'type': 'object',
    'additionalProperties': {
        'type': 'object',
        'default': {},
        'additionalProperties': False,
        'patternProperties': {
            r'\w[\w-]*': {  # os class
                'type': 'object',
                'default': {},
                'patternProperties': {
                    r'\w[\w-]*': { # package name
                        'type': 'array',
                        'default': [],
                        'properties': {
                            'spec': {'type': 'string'},
                            'package': {'type': 'string'}
                        }
                    }
                },
                'properties': {
                    'regex-matching-list': {
                        'type': 'array',
                        'default': [],
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'shims': {
                                    'type': 'array',
                                    'default': [],
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'spec': {'type': 'string'},
                                            'package': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                'required': ['regex-matching-list']
#                'additionalProperties': {
#                },
#                'items': {
#                    'type': 'object',
#                    'properties': {
#                        'name': {'type': 'string'},
#                        'regex': {'type': 'boolean'},
#                        'demangler': {'type': 'string'},
#                        'shims': {
#                            'type': 'array',
#                            'default': [],
#                            'properties': {
#                                'spec': {'type': 'string'},
#                                'pattern': {'type': 'string'}
#                            }
#                        }
#                    }
#                }
                #'additionalProperties': False,
                #'patternProperties': {
                #    r'\w[\w-]*': { # spack package name
                #        'type': 'array',
                #        'default': [],
                #        'items': {
                #            'type': 'object',
                #            'properties': {
                #                'spec': {'type': 'string'},
                #                'pattern': {'type': 'string'},
                #                'premangler': {'type': 'string'},
                #                'demangler': {'type': 'string'}
                #            }
                #        }
                #    }
                #}
            }
        }
    }
}
