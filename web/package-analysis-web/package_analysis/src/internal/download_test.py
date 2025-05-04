from pkgmanager.npm import npm_pkg_manager
from pkgmanager.pypi import pypi_pkg_manager
from pkgmanager.crates_io import crates_pkg_manager
from pkgmanager.rubygems import rubygems_pkg_manager
from pkgmanager.packagist import packagist_pkg_manager
from pkgmanager.maven import maven_pkg_manager

import os

def test_npm():
    # Fetch the latest version of a package
    package_name = "express"
    latest_package = npm_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "4.18.2"
    specific_package = npm_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    archive_path = npm_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    npm_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {output_directory}")

def test_pypi():
    
    package_name = "requests"
    latest_package = pypi_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "2.29.0"
    specific_package = pypi_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    os.makedirs(download_directory, exist_ok=True)
    archive_path = pypi_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    _, outputdir = pypi_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {outputdir}")

def test_crates():

    package_name = "tokio"
    latest_package = crates_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "1.44.1"
    specific_package = crates_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    archive_path = crates_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    crates_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {output_directory}")

def test_rubygems():
    
    package_name = "rails_autolink"
    latest_package = rubygems_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "1.1.8"
    specific_package = rubygems_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    archive_path = rubygems_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    rubygems_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {output_directory}")


def test_packagist():

    package_name = "tracy/tracy"
    latest_package = packagist_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "v2.10.10"
    specific_package = packagist_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    archive_path = packagist_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    packagist_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {output_directory}")

def test_maven():
    package_name = "com.google.guava:guava"
    latest_package = maven_pkg_manager.latest(package_name)
    print(f"Latest package: {latest_package}")

    # Fetch a specific version of a package
    specific_version = "33.4.8-jre"
    specific_package = maven_pkg_manager.package(package_name, specific_version)
    print(f"Specific package: {specific_package}")

    # # Download the package archive
    download_directory = "./test_download"
    archive_path = maven_pkg_manager.download_archive(package_name, specific_version, download_directory)
    print(f"Downloaded archive to: {archive_path}")

    # # Extract the archive (if implemented)
    output_directory = "./test_extracted"
    os.makedirs(output_directory, exist_ok=True)

    maven_pkg_manager.extract_archive(archive_path, output_directory)
    print(f"Extracted archive to: {output_directory}")


if __name__ == "__main__":
    test_pypi()
    # test_crates()