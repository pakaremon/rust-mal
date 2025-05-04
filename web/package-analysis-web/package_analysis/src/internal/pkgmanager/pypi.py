import requests
from .ecosystem import PkgManager, Ecosystem
from .utils import Extracter


def get_pypi_latest(pkg_name):
    response = requests.get(f"https://pypi.org/pypi/{pkg_name}/json")
    response.raise_for_status()
    data = response.json()
    return data["info"]["version"]

def get_pypi_archive_url(pkg_name, version):
    response = requests.get(f"https://pypi.org/pypi/{pkg_name}/{version}/json")
    response.raise_for_status()
    data = response.json()
    
    for url in data['urls']:
        if url['packagetype'] == "sdist":
            return url['url']


pypi_pkg_manager = PkgManager(
    ecosystem=Ecosystem.PYPI,
    latest_version_func=get_pypi_latest,
    archive_url_func=get_pypi_archive_url,
    archive_filename_func=PkgManager.default_archive_filename,
    extract_archive_func=Extracter.extract_archive_file,
)