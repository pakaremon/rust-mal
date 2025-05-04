import requests
from .ecosystem import PkgManager, Ecosystem
from .utils import Extracter

def get_rubygems_latest(pkg_name):
    response = requests.get(f"https://rubygems.org/api/v1/gems/{pkg_name}.json")
    response.raise_for_status()
    data = response.json()
    return data['version']

def get_rubygems_archive_url(pkg_name, version):
   return f"https://rubygems.org/gems/{pkg_name}-{version}.gem"



rubygems_pkg_manager = PkgManager(
    ecosystem=Ecosystem.RUBYGEMS,
    latest_version_func=get_rubygems_latest,
    archive_url_func=get_rubygems_archive_url,
    archive_filename_func=PkgManager.default_archive_filename,
    extract_archive_func=Extracter.extract_gem,
)