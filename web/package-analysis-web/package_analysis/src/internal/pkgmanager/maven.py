import requests
from xml.etree import ElementTree
from .ecosystem import PkgManager, Ecosystem
from .utils import Extracter

def get_maven_latest(pkg_name):
    """
    Fetches the latest version of a Maven package.
    """
    group_id, artifact_id = parse_maven_package(pkg_name)
    url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/maven-metadata.xml"
    response = requests.get(url)
    response.raise_for_status()

    # Parse the XML response
    tree = ElementTree.fromstring(response.content)
    latest = tree.findtext("versioning/latest")
    if not latest:
        raise ValueError(f"Could not find the latest version for package: {pkg_name}")
    return latest


def get_maven_archive_url(pkg_name, version):
    """
    Constructs the URL to download the Maven package JAR file.
    """
    group_id, artifact_id = parse_maven_package(pkg_name)
    jar_url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{version}/{artifact_id}-{version}.jar"
    return jar_url


def get_maven_archive_filename(pkg_name, version, _:str):
    """
    Constructs the filename for the Maven package JAR file.
    """
    _, artifact_id = parse_maven_package(pkg_name)
    return f"{artifact_id}-{version}.jar"


def parse_maven_package(pkg):
    """
    Parses a Maven package string in the format 'groupID:artifactID'.
    """
    parts = pkg.split(":")
    if len(parts) != 2:
        return "", ""
    return parts[0], parts[1]


# Define the Maven package manager
maven_pkg_manager = PkgManager(
    ecosystem=Ecosystem.MAVEN,
    latest_version_func=get_maven_latest,
    archive_url_func=get_maven_archive_url,
    archive_filename_func=get_maven_archive_filename,
    extract_archive_func=Extracter.extract_jar_file,
)