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
"""The variant module contains data structures that are needed to manage
variants both in packages and in specs.
"""

import cStringIO
import csv
import inspect
import llnl.util.lang as lang
import spack.error as error


class Variant(object):
    """Represents a variant in a package, as declared in the
    variant directive.
    """

    def __init__(self, name, default, description, values=(True, False), exclusive=True):  # NOQA: ignore=E501
        """Initialize a package variant.

        :param str name: name of the variant
        :param str default: default value for the variant in case
        nothing has been specified
        :param str description: purpose of the variant
        :param sequence values: sequence of allowed values or a callable
        accepting a single value as argument and returning True if the
        value is good, False otherwise
        :param bool exclusive: whether multiple CSV are allowed
        """
        self.name = name
        self.default = default
        self.description = str(description)

        if inspect.isroutine(values):
            # If 'values' is a callable, assume it is a custom validator
            # and reset the values to be explicit during debug
            self.validator = values
            self.values = None
        else:
            # Otherwise assume values is the set of allowed explicit values
            self.values = tuple(values)
            allowed = self.values + (self.default,)
            self.validator = lambda x: x in allowed

        self.exclusive = exclusive

    def validate_or_raise(self, vspec, pkg=None):
        """Validate a variant spec against this package variant. Raises an
        exception if any error is found.

        :param VariantSpec vspec: instance to be validated
        :param Package pkg: the package that required the validation,
        if available

        :raises InconsistentValidationError: if vspec.name doesn't
        match self.name
        :raises MultipleValuesInExclusiveVariantError: if vspec has
        multiple values but self.exclusive ==True
        :raises InvalidVariantValueError: if vspec.value contains
        invalid values
        """
        # Check the name of the variant
        if self.name != vspec.name:
            raise InconsistentValidationError(vspec, self)
        # Check the values of the variant spec
        value = vspec.value
        if isinstance(vspec.value, bool):
            value = (vspec.value,)
        # If the value is exclusive there must be at most one
        if self.exclusive and len(value) != 1:
            raise MultipleValuesInExclusiveVariantError(vspec, pkg)
        # Check and record the values that are not allowed
        not_allowed_values = [x for x in value if not self.validator(x)]
        if not_allowed_values:
            raise InvalidVariantValueError(self, not_allowed_values, pkg)


@lang.key_ordering
class VariantSpec(object):
    """Variants are named, build-time options for a package. Names depend
    on the particular package being built, and each named variant can have
    different (and possibly multiple) values.
    """

    def __init__(self, name, value):
        self.name = name
        # Stores the original value passed to initialize this instance
        self._original_value = value
        # Stores 'value' after a bit of massaging
        # done by the property setter
        self._value = None
        # Invokes property setter
        self.value = value

    @property
    def value(self):
        """Returns either a boolean or a tuple of strings

        :return: either a boolean or a tuple of strings
        :rtype: bool or tuple
        """
        return self._value

    @value.setter
    def value(self, value):
        # Store the original value
        self._original_value = value
        # If value is a string representation of a boolean, turn
        # it to a boolean
        if str(value).upper() == 'TRUE':
            self._value = True
        elif str(value).upper() == 'FALSE':
            self._value = False
        # Otherwise store a tuple of CSV string representations
        # Tuple is necessary here instead of list because the
        # values need to be hashed
        else:
            f = cStringIO.StringIO(str(value))
            try:
                t = next(csv.reader(f, skipinitialspace=True))
            except StopIteration:
                t = ['']
            # With multi-value variants it is necessary
            # to remove duplicates and give an order
            # to a set
            self._value = tuple(sorted(set(t)))

    def _cmp_key(self):
        return self.name, self.value

    def copy(self):
        """Returns an instance of VariantSpec equivalent to self

        :return: a copy of self
        :rtype: VariantSpec

        >>> a = VariantSpec('foo', True)
        >>> b = a.copy()
        >>> assert a == b
        >>> assert a is not b
        """
        return VariantSpec(self.name, self._original_value)

    def satisfies(self, other):
        """Returns true if the other.value is a strict subset of self.
        Does not try to validate.

        :param VariantSpec other: constraint to be met for the method to
        return True
        :return: True or False
        :rtype: bool
        """
        single_value_satisfies = self.value == other.value
        multi_value_satisfies = False
        if isinstance(self.value, tuple):
            not_satisfied = set(other.value) - set(self.value)
            multi_value_satisfies = len(not_satisfied) == 0
        return single_value_satisfies or multi_value_satisfies

    def compatible(self, other):
        """Returns True if self and other are compatible, False otherwise.
        As there is no semantic check, two VariantSpec are compatible if
        either they contain the same value or they are both multi-valued.

        :param VariantSpec other: instance against which we test compatibility
        :return: True or False
        :rtype: bool
        """
        single_value_compatible = self.value == other.value
        multi_value_compatible = True
        for x in (self.value, other.value):
            multi_value_compatible &= isinstance(x, tuple)
        return single_value_compatible or multi_value_compatible

    def constrain(self, other):
        """Modify self to match all the constraints for other if both
        instances are multi-valued. Returns True if self changed,
        False otherwise.

        :param VariantSpec other: instance against which we constrain self
        :return: True or False
        :rtype: bool
        """
        changed = False
        if isinstance(self.value, tuple) and isinstance(other.value, tuple):
            old_value = self.value
            self.value = ','.join(self.value + other.value)
            return old_value != self.value
        return changed

    def yaml_entry(self):
        """Returns a key, value tuple suitable to be an entry in a yaml dict

        :return: (name, value_representation)
        :rtype: tuple
        """
        v = self.value
        if isinstance(self.value, tuple):
            v = ','.join(self.value)
        return self.name, v

    def __contains__(self, item):
        if isinstance(self._value, bool):
            return item is self._value
        return item in self._value

    def __repr__(self):
        cls = type(self)
        return '{0.__name__}({1}, {2})'.format(
            cls, repr(self.name), repr(self._original_value)
        )

    def __str__(self):
        if isinstance(self.value, bool):
            return '{0}{1}'.format('+' if self.value else '~', self.name)
        else:
            return ' {0}={1} '.format(
                self.name, ','.join(str(x) for x in self.value))


class VariantMap(lang.HashableMap):
    """Map containing VariantSpec instances. New values can be added only
    if the key is not already present.
    """

    def __init__(self, spec):
        super(VariantMap, self).__init__()
        self.spec = spec

    def __setitem__(self, name, vspec):
        # Raise a TypeError if vspec is not of the right type
        if not isinstance(vspec, VariantSpec):
            msg = 'VariantMap accepts only values of type VariantSpec'
            raise TypeError(msg)
        # Raise an error if the variant was already in this map
        if name in self.dict:
            msg = 'Cannot specify variant "{0}" twice'.format(name)
            raise DuplicateVariantError(msg)
        # Raise an error if name and vspec.name don't match
        if name != vspec.name:
            msg = 'Inconsistent key "{0}", must be "{1}" to match VariantSpec'
            raise KeyError(msg.format(name, vspec.name))
        # Set the item
        super(VariantMap, self).__setitem__(name, vspec)

    def satisfies(self, other, strict=False):
        """Returns True if this VariantMap is more constrained than other,
        False otherwise.

        :param VariantMap other: VariantMap to satisfy
        :param bool strict: if True return False if a key is in other and
        not in self, otherwise discard that key and proceed with evaluation

        :return: True or False
        :rtype: bool
        """
        to_be_checked = [k for k in other]
        if not (strict or self.spec._concrete):
            to_be_checked = filter(lambda x: x in self, to_be_checked)

        return all(
            k in self and self[k].satisfies(other[k]) for k in to_be_checked
        )

    def constrain(self, other):
        """Add all variants in other that aren't in self to self. Also
        constrain all multi-valued variants that are already present.
        Return True if self changed, False otherwise

        :param VariantMap other: instance against which we constrain self
        :return: True or False
        :rtype: bool
        :raises UnsatisfiableVariantSpecError: if a constraint is incompatible
        with self
        """
        if other.spec._concrete:
            for k in self:
                if k not in other:
                    raise UnsatisfiableVariantSpecError(self[k], '<absent>')

        changed = False
        for k in other:
            if k in self:
                # If they are not compatible raise an error
                if not self[k].compatible(other[k]):
                    raise UnsatisfiableVariantSpecError(self[k], other[k])
                # If they are compatible merge them
                changed = self[k].constrain(other[k])
            else:
                # If it is not present copy it straight away
                self[k] = other[k].copy()
                changed = True

        return changed

    @property
    def concrete(self):
        return self.spec._concrete or all(
            v in self for v in self.spec.package_class.variants)

    def copy(self):
        """Return an instance of VariantMap equivalent to self

        :return: a copy of self
        :rtype: VariantMap
        """
        clone = VariantMap(self.spec)
        for name, variant in self.items():
            clone[name] = variant.copy()
        return clone

    def __str__(self):
        sorted_keys = sorted(self.keys())
        pad = ' ' if len(self) > 0 else ''
        return "%s%s%s" % (
            pad, ' '.join(str(self[key]) for key in sorted_keys), pad)


class DuplicateVariantError(error.SpecError):
    """Raised when the same variant occurs in a spec twice."""


class UnknownVariantError(error.SpecError):
    """Raised when an unknown variant occurs in a spec."""
    def __init__(self, pkg, variant):
        super(UnknownVariantError, self).__init__(
            'Package {0} has no variant {1}!'.format(pkg, variant)
        )


class InconsistentValidationError(error.SpecError):
    def __init__(self, vspec, variant):
        msg = 'trying to validate variant "{0.name}" with the validator of "{1.name}"'  # NOQA: ignore=E501
        super(InconsistentValidationError, self).__init__(
            msg.format(vspec, variant)
        )


class MultipleValuesInExclusiveVariantError(error.SpecError):
    def __init__(self, variant, pkg):
        msg = 'multiple values are not allowed for variant "{0.name}"{1}'
        pkg_info = ''
        if pkg is not None:
            pkg_info = ' in package "{0}"'.format(pkg.name)
        super(MultipleValuesInExclusiveVariantError, self).__init__(
            msg.format(variant, pkg_info)
        )


class InvalidVariantValueError(error.SpecError):
    """Raised when a valid variant has at least an invalid value."""
    def __init__(self, variant, invalid_values, pkg):
        msg = 'invalid values for variant "{0.name}"{2}: {1}\n'
        pkg_info = ''
        if pkg is not None:
            pkg_info = ' in package "{0}"'.format(pkg.name)
        super(InvalidVariantValueError, self).__init__(
            msg.format(variant, invalid_values, pkg_info)
        )


class UnsatisfiableVariantSpecError(error.UnsatisfiableSpecError):
    """Raised when a spec variant conflicts with package constraints."""
    def __init__(self, provided, required):
        super(UnsatisfiableVariantSpecError, self).__init__(
            provided, required, "variant")
