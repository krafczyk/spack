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

class NoVersions(spack.error.SpackError):
    def __init__(self):
        super(NoVersions, self).__init__("""No versions were found for this package!""")

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
        self.options = []

    def add_option(self, item):
        self.options.append(item)

    def prioritize_option(self, item):
        # Move option to the front of the list
        self.options.remove(item)
        self.options.insert(0, item)

class VariantEnumeration(OptionEnumeration):
    """This is for variants of a package"""
    def __init__(self, variant):
        super(VariantEnumeration, self).__init__()

        self.name = variant.name
        self.values = variant.values
        self.default = variant.default
        if self.values is not None:
            for value in self.values:
                self.add_option(value)
            self.prioritize_option(self.default)

class DependencyEnumeration(OptionEnumeration):
    """This is for dependencies of a package"""
    def __init__(self):
        super(DependencyEnumeration, self).__init__()

class DependencyEncapsulation(object):
    """This object encapsulates all relavant information about a dependency"""
    def __init__(self, dep_spec, dep_type, clause):
        self.dep_spec = dep_spec # A spec of requirements for the dep itself
        self.dep_type = dep_type # The type of dependency it is
        self.clause = clause # clause which must be satisfied for this dependency to be used

    def __eq__(self, rhs):
        if self.dep_spec == rhs.dep_spec and \
           self.dep_type == rhs.dep_type and \
           self.clause == rhs.clause:
            return True
        else:
            return False

class PackageEnumeration(object):
    """We will contain a package's current state"""
    def __init__(self, spec):
        # Check that the spec exists or is virtual
        self.name = spec.name
        self._init_spec = spec
        self._initial_version_constraints = [] # contains the initial set of constraints on the package version
        self._initial_compiler_constraints = [] # contains the initial set of constraints on the compiler version
        self._initial_variant_constraints = [] # contains the initial set of constraints on the variants
        self._dependencies_by_package = {} # contains a dictionary of possible dependencies by package
        self._variants = [] # A list of variants for this package

        self.add_constraints_from_spec(spec)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._spec = spack.spack.Spec(self._name)

    @property
    def spec(self):
        return self._spec

    def initialize_build_options(self):
        pkg_versions = self._init_spec.package_class.versions
        usable = [v for v in pkg_versions
                  if any(v.satisfies(sv) for sv in self._init_spec.versions)]

        yaml_prefs = PackagePrefs(self.name, 'version')

        # The keys below show the order of precedence of factors used
        # to select a version when concretizing.  The item with
        # the "largest" key will be selected.
        #
        # NOTE: When COMPARING VERSIONS, the '@develop' version is always
        #       larger than other versions.  BUT when CONCRETIZING,
        #       the largest NON-develop version is selected by default.
        keyfn = lambda v: (
            # ------- Special direction from the user
            # Respect order listed in packages.yaml
            -yaml_prefs(v),

            # The preferred=True flag (packages or packages.yaml or both?)
            pkg_versions.get(Version(v)).get('preferred', False),

            # ------- Regular case: use latest non-develop version by default.
            # Avoid @develop version, which would otherwise be the "largest"
            # in straight version comparisons
            not v.isdevelop(),

            # Compare the version itself
            # This includes the logic:
            #    a) develop > everything (disabled by "not v.isdevelop() above)
            #    b) numeric > non-numeric
            #    c) Numeric or string comparison
            v)
        usable.sort(key=keyfn, reverse=True)

        # Test for empty version list
        if len(usable) == 0:
            print("Package version:")
            if not self._init_spec.versions.concrete:
                print(self._init_spec.versions)
                #raise NoVersions()
            print(self._init_spec.version)
        else:
            print("Known package versions for spec: {}".format(self.spec))
            for v in usable:
                print(v)

    def add_dependency(self, dependency):
        dep_name = dependency.dep_spec.name
        return add_to_list(dependency, self._dependencies_by_package.setdefault(dep_name, []))

    def add_constraints_from_spec(self, spec):
        return self._init_spec.constrain(spec)
        changed = False
        if spec.versions:
            changed |= add_to_list(spec.versions, self._initial_version_constraints)
        if spec.compiler:
            changed |= add_to_list(spec.compiler, self._initial_compiler_constraints)
        if spec.variants:
            changed |= add_to_list(spec.variants, self._initial_variant_constraints)
        return changed

    def add_variant(self, variant):
        for var in self._variants:
            if var.name == variant.name:
                return False
        self._variants.append(VariantEnumeration(variant))
        return True

    def show(self):
        print("Package: {}".format(self._name))
        print("Known initial required spec:")
        print(self._init_spec)
        #print_version = False
        #if len(self._initial_version_constraints) == 1:
        #    if self._initial_version_constraints[0].__str__() != ":":
        #        print_version = True
        #else:
        #    print_version = True
        #if print_version:
        #    print("Version:")
        #    for constraint in self._initial_version_constraints:
        #        if constraint.__str__() != ":":
        #            print(constraint)
        #if len(self._initial_compiler_constraints) != 0:
        #    print("Compiler:")
        #    for constraint in self._initial_compiler_constraints:
        #        print(constraint)
        #if len(self._initial_variant_constraints) != 0:
        #    print("Variants:")
        #    for constraint in self._initial_variant_constraints:
        #        print(constraint)
        print("Possible Dependencies:")
        for package_name in self._dependencies_by_package:
            print("{} dependencies:".format(package_name))
            for dependency in self._dependencies_by_package[package_name]:
                print("clause: {} dep: {} type: {}".format(dependency.clause, dependency.dep_spec, dependency.dep_type))
        print("Possible Variant Settings:")
        for variant in self._variants:
            print("Variant {}:".format(variant.name))
            for option in variant.options:
                print(option)

class VirtualPackageEnumeration(object):
    """We will contain a package's current state"""
    def __init__(self, spec):
        # Check that the spec exists or is virtual
        self.name = spec.name
        self._possible_providers = []
        self._active = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def add_provider(self, provider):
        return add_to_list(provider, self._possible_providers)

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
        self.initialize_build_options()

    def get_package(self, name):
        for package in self._packages:
            if package.name == name:
                return package
        return None

    def get_virtual_package(self, name):
        for package in self._virtual_packages:
            if package.name == name:
                return package
        return None

    def initialize_build_options(self):
        for package in self._packages:
            package.initialize_build_options()

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
                package._init_spec.constrain(spec)
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

        #Crawl through each package and add missing dependencies, constraints, and variants
        while True:
            changed = False

            for package in self._packages:
                pkg = package._init_spec.package

                for dep_name in pkg.dependencies:
                    dep_name_spec = spack.spec.Spec(dep_name)
                    if dep_name_spec.virtual:
                        # Add dependent virtual package by plain name
                        dep_package = self.get_virtual_package(dep_name)
                        if dep_package is None:
                            dep_package = VirtualPackageEnumeration(dep_name_spec)
                            self._virtual_packages.append(dep_package)
                            changed = True

                    else:
                        # Add dependent package by plain name
                        dep_package = self.get_package(dep_name)
                        if dep_package is None:
                            dep_package = PackageEnumeration(dep_name_spec)
                            self._packages.append(dep_package)
                            changed = True

                    # Add full description of dependencies to package
                    for clause in pkg.dependencies[dep_name]:
                        full_dep = pkg.dependencies[dep_name][clause]
                        changed |= package.add_dependency(DependencyEncapsulation(full_dep.spec, full_dep.type, clause))

                for variant_name in pkg.variants:
                    variant = pkg.variants[variant_name]
                    changed |= package.add_variant(variant)

            for package in self._virtual_packages:
                package_spec = package.name
                # Find providers for virtual packages
                for provider in spack.repo.providers_for(package_spec):
                    changed |= package.add_provider(provider)
                    provider_package = self.get_package(provider.name)
                    if provider_package is None:
                        provider_package = PackageEnumeration(provider)
                        self._packages.append(provider_package)
                        changed = True

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
            if spec.name == package.name:
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
            package.show()

    def concretize(self):
        # First
        pass
