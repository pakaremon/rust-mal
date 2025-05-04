from .npmpackage import NpmPackage, npmPackageRelease, npmPackageNotFoundException
from .pypackage import PyPackage, PyPackageRelease, PyPackageNotFoundException
from .rubypackage import RubyPackage, RubyPackageRelease, RubyPackageNotFoundException
from .cratepackage import CratePackage, CratePackageRelease, CratePackageNotFoundException
from .mavenpackage import MavenPackage, MavenPackageRelease, MavenPackageNotFoundException
import os
import json
from .npmpackage import NpmPackage, npmPackageNotFoundException
from .pypackage import PyPackage, PyPackageNotFoundException
from .rubypackage import RubyPackage, RubyPackageNotFoundException
from .cratepackage import CratePackage, CratePackageNotFoundException
from .mavenpackage import MavenPackage, MavenPackageNotFoundException




class EcosystemPackageManager:
    """
    A class to manage different ecosystems and provide a unified interface for package analysis.
    """

    @staticmethod
    def get_package_class(ecosystem: str):
        """
        Returns the appropriate package class based on the ecosystem name.
        """
        match ecosystem:
            case "npm":
                return NpmPackage
            case "pypi":
                return PyPackage
            case "ruby":
                return RubyPackage
            case "crate":
                return CratePackage
            case "maven":
                return MavenPackage
            case _:
                raise ValueError(f"Unsupported ecosystem: {ecosystem}")

    @classmethod
    def create_analysis_for_package(cls, package_name: str, package_version: str = None, ecosystem: str = None, checked: bool = False, **options):
        """
        Creates a MaliciousCodePackageAnalyzer object for analyzing a package.

        Parameters:
            package_name (str): The name of the package to analyze.
            package_version (str): The version of the package. Defaults to None (latest version).
            ecosystem (str): The ecosystem of the package (e.g., npm, pypi, ruby, crate, maven).
            checked (bool): If True, no exception is raised if the package cannot be found. Defaults to False.

        Named options:
            tmp_folder (str): Temporary folder path.
            repo_folder (str): Git repository folder path.
            keep_tmp_folder (bool): If True, temporary folder is not deleted. Defaults to False.
            cache_folder (str): Cache folder path for artifacts and repositories.
            cache_metadata_folder (str): Cache folder path for package metadata.

        Returns:
            MaliciousCodePackageAnalyzer: An object for analyzing the requested package.
        """
        cls.__logger.info(f"Searching package '{package_name}' version: {'<LATEST>' if package_version is None else package_version}")

        if not ecosystem:
            raise ValueError("Ecosystem must be specified")

        PackageClass = cls.get_package_class(ecosystem)

        try:
            if "cache_metadata_folder" in options:
                cache_metadata_folder = options["cache_metadata_folder"]
                if not os.path.exists(cache_metadata_folder):
                    os.makedirs(cache_metadata_folder)
                data_file = os.path.join(cache_metadata_folder, f"{package_name}_{package_version if package_version else 'LATEST'}")

                if not os.path.exists(data_file):
                    package_data = PackageClass._getPackageMetadata(package_name, package_version)
                    with open(data_file, "w") as f:
                        f.write(json.dumps(package_data))
                else:
                    cls.__logger.debug(f"Loading cached package data {data_file}")
                    with open(data_file, "rb") as f:
                        package_data = json.loads(f.read())

                package = PackageClass(package_data)
            else:
                package = PackageClass.searchPackage(package_name, package_version)
                cls.__logger.info(f"Package '{package.getName()}' version: {package.getVersion()} FOUND")

            return MaliciousCodePackageAnalyzer(package, **options)
        except (npmPackageNotFoundException, PyPackageNotFoundException, RubyPackageNotFoundException, CratePackageNotFoundException, MavenPackageNotFoundException) as e:
            cls.__logger.error(f"Package '{package_name}' version: {'<LATEST>' if package_version is None else package_version} NOT FOUND {e}")
            if checked:
                return None
            else:
                raise e

