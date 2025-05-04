from .npm import npm_pkg_manager
from .pypi import pypi_pkg_manager
from .crates_io import crates_pkg_manager
from .rubygems import rubygems_pkg_manager
from .packagist import packagist_pkg_manager
from .maven import maven_pkg_manager


def get_pkg_manager(ecosystem):
    managers = {
        "npm": npm_pkg_manager,
        "pypi": pypi_pkg_manager,
        "maven": maven_pkg_manager,
        "rubygems": rubygems_pkg_manager,
        "packagist": packagist_pkg_manager,
        "crates.io": crates_pkg_manager,
    }
    return managers.get(ecosystem.lower())

def pkg(name, version, ecosystem):
    '''
        return a class Pkg in file ecosystem.py which contain package name, version and manager
    '''
    manager = get_pkg_manager(ecosystem)
    if not manager:
        raise ValueError(f"Unsupported ecosystem: {ecosystem}")
    return manager.package(name, version)