import requests
from .ecosystem import PkgManager, Ecosystem
from  .utils import Extracter


def get_crates_latest(pkg_name):
    response = requests.get(f"https://crates.io/api/v1/crates/{pkg_name}/versions")
    response.raise_for_status()
    data = response.json()
    return data['versions'][0]['num']

def get_crates_archive_url(pkg_name, version):
    return f"https://crates.io/api/v1/crates/{pkg_name}/{version}/download"

    
def get_crates_archive_filename(pkg_name, version, _):
    return ' '.join([pkg_name, "-", version, ".tar.gz"])


crates_pkg_manager = PkgManager(
    ecosystem=Ecosystem.CRATES_IO,
    latest_version_func=get_crates_latest,
    archive_url_func=get_crates_archive_url,
    archive_filename_func=get_crates_archive_filename,
    extract_archive_func=Extracter.extract_archive_file,
)