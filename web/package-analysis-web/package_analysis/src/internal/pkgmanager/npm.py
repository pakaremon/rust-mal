import requests
from .ecosystem import PkgManager, Ecosystem
from .utils import Extracter


def get_npm_latest(pkg_name):
    response = requests.get(f"https://registry.npmjs.org/{pkg_name}")
    response.raise_for_status()
    data = response.json()
    return data["dist-tags"]["latest"]

def get_npm_archive_url(pkg_name, version):
    response = requests.get(f"https://registry.npmjs.org/{pkg_name}/{version}")
    response.raise_for_status()
    data = response.json()
    return data["dist"]["tarball"]

def get_npm_archive_filename(pkg_name, version, _):
    cleaned_name = pkg_name.replace("/", "-")
    return f"{cleaned_name}-{version}.tgz"

npm_pkg_manager = PkgManager(
    ecosystem=Ecosystem.NPM,
    latest_version_func=get_npm_latest,
    archive_url_func=get_npm_archive_url,
    archive_filename_func=get_npm_archive_filename,
    extract_archive_func=Extracter.extract_archive_file,
)