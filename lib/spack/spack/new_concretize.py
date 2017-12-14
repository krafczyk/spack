import copy

import spack
import spack.spec
import spack.compilers
import spack.architecture
import spack.error
from spack.version import ver, Version, VersionList, VersionRange
from spack.package_prefs import PackagePrefs, spec_externals, is_spec_buildable

class VirtualPacakgesUnsupported(spack.error.SpackError):
    def __init__(self):
        super(VirtualPacakgesUnsupported, self).__init__("""This method does not support virtual packages for now.""")

class AnonymousSpecsUnsupported(spack.error.SpackError):
    def __init__(self):
        super(VirtualPacakgesUnsupported, self).__init__("""This method does not support anonymous specs for now.""")

class IncorrectSpecType(spack.error.SpackError):
    def __init__(self):
        super(IncorrectSpecType, self).__init__("""The incorrect spec was passed!""")

def add_to_list(item, the_list):
    if item in the_list:
        return False
    else:
        the_list.append(item)
        return True

class OptionEnumeration(object):
    """Here we detail options for a package"""
    def __init__(self):
        pass

class VariantEnumeration(OptionEnumeration):
    """This is for variants of a package"""
    def __init__(self):
        super(VariantEnumeration, self).__init__()

class DependencyEnumeration(OptionEnumeration):
    """This is for dependencies of a package"""
    def __init__(self):
        super(DependencyEnumeration, self).__init__()

class DependencyEnumeration(OptionEnumeration):
    """This is for dependencies of a package"""
    def __init__(self):
        super(DependencyEnumeration, self).__init__()

class PackageEnumeration(object):
    """We will contain a package's current state"""
    def __init__(self, spec):
        # Check that the spec exists or is virtual
        self._name = spec.name
        self._init_spec = spec
        self._initial_version_constraints = []
        self._initial_compiler_constraints = []
        self._initial_variant_constraints = []
        self._dependencies_with_clauses = []
        self._required_constraints = []
        self._active = True

        self.add_constraints_from_spec(spec)

    def add_dependency_and_clause(self, dependency, clause=""):
        new_item = [dependency, clause]
        return add_to_list(new_item, self._dependencies_with_clauses)

    def add_constraints_from_spec(self, spec):
        changed = False
        if spec.versions:
            changed |= add_to_list(spec.versions, self._initial_version_constraints)
        if spec.compiler:
            changed |= add_to_list(spec.compiler, self._initial_compiler_constraints)
        if spec.variants:
            changed |= add_to_list(spec.variants, self._initial_variant_constraints)
        return changed

    def show(self):
        print("Package: {}".format(self._name))
        print("Known initial constraints:")
        print("Version:")
        for constraint in self._initial_version_constraints:
            print(constraint)
        print("Compiler:")
        for constraint in self._initial_compiler_constraints:
            print(constraint)
        print("Variants:")
        for constraint in self._initial_variant_constraints:
            print(constraint)

class VirtualPackageEnumeration(object):
    """We will contain a package's current state"""
    def __init__(self, spec):
        # Check that the spec exists or is virtual
        self._name = spec.name
        self._possible_providers = []
        self._active = True

    def show(self):
        print("Virtual Package: {}".format(self._name))
        print("Possible Providers:")
        for provider in self._possible_providers:
            print(provider)

class Constraint(object):
    """This will represent a constraint on a spec"""
    def __init__(self, spec):
        if spec.name is not None:
            raise RuntimeError("Constraints must be anonymous specs")
        self._spec = spec

class Concretizer(object):
    """We need to carry state with this concretizer"""
    def __init__(self, specs):
        self._initial_specs = []
        self._leaf_packages = []
        self._needed_dep_packages = []
        self._packages = []
        self._virtual_packages = []

        # Fill leaves and needed deps
        for spec in specs:
            self._initial_specs.append(spec)
            self.add_spec(spec)

        self.create_package_representations()

    def get_package(self, name):
        for package in self._packages:
            if package._name == name:
                return package
        return None

    def get_virtual_package(self, name):
        for package in self._virtual_packages:
            if package._name == name:
                return package
        return None

    def create_package_representations(self):
        changed = False
        
        leaf_list = copy.copy(self._leaf_packages)
        needed_dep_list = copy.copy(self._needed_dep_packages)
        # Add leaf packages
        while len(leaf_list) != 0:
            spec = leaf_list[0]
            package = self.get_package(spec.name)
            if package is None:
                package = PackageEnumeration(spec)
                self._packages.append(package)
            else:
                package.add_constraints_from_spec(spec)
            leaf_list.pop(0)

        # Add needed dep packages
        while len(needed_dep_list) != 0:
            spec = needed_dep_list[0]
            package = self.get_package(spec.name)
            if package is None:
                package = PackageEnumeration(spec)
                self._packages.append(package)
            else:
                package.add_constraints_from_spec(spec)
            needed_dep_list.pop(0)

        #Crawl through each package and add missing dependencies and constraints
        while True:
            changed = False

            for package in self._packages:
                pkg = package._init_spec.package

                for dep_name in pkg.dependencies:
                    # Add dep_name package
                    dep_name_spec = spack.spec.Spec(dep_name)
                    if dep_name_spec.virtual:
                        dep_package = self.get_virtual_package(dep_name)
                        if dep_package is None:
                            dep_package = VirtualPackageEnumeration(dep_name_spec)
                            self._virtual_packages.append(dep_package)
                            changed = True

                    else:
                        dep_package = self.get_package(dep_name)
                        if dep_package is None:
                            dep_package = PackageEnumeration(dep_name_spec)
                            self._packages.append(dep_package)
                            changed = True

                        changed |= dep_package.add_constraints_from_spec(dep_name_spec)

                        for dep_clause in pkg.dependencies[dep_name]:
                            dep_clause_spec = spack.spec.Spec(dep_clause)
                            #dep = pkg.dependencies[dep_name][dep_clause]
                            changed |= package.add_dependency_and_clause(dep_name_spec, dep_clause_spec)

            if not changed:
                break
            
    def add_spec(self, spec, explicit_dep=False):
        # We're not supporting virtual packages for now.
        if spec.virtual:
            raise VirtualPackagesUnsupported()
        else:
            if spec.name is not None:
                if explicit_dep:
                    self._needed_dep_packages.append(spack.spec.Spec(spec.format()))
                else:
                    self._leaf_packages.append(spack.spec.Spec(spec.format()))
                for dep in spec.dependencies():
                    self.add_spec(dep, explicit_dep=True)
            else:
                raise AnonymousSpecsUnsupported()

    def add_package(self, spec):
        # Get package
        pkg = spec.package
        existing_package = None
        for package in self._packages:
            if spec.name == package._name:
                existing_package = package
        if existing_package is not None:
            existing_package.add_constraints_from_spec(spec)
        else:
            self._packages.append(PackageEnumeration(spec))

    def show(self):
        print("Initial State:")
        print("Leaf Packages:")
        for spec in self._leaf_packages:
            print(spec)
        print("Needed dependencies:")
        for spec in self._needed_dep_packages:
            print(spec)
        print("Packages which might be in tree:")
        for package in self._packages:
            package.show()
        print("Virtual packages which might be in tree:")
        for package in self._virtual_packages:
            print(package._name)



    def concretize(self):
        # First
        pass
