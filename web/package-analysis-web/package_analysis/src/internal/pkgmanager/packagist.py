import requests
from .ecosystem import PkgManager, Ecosystem
from .utils import Extracter
from datetime import datetime


def get_packagist_latest(pkg_name):
    response = requests.get(f"https://repo.packagist.org/p2/{pkg_name}.json")
    response.raise_for_status()
    data = response.json()
    
    last_time = None
    latest_version = ""
    for versions in data['packages'].keys():
        for v in data['packages'][versions]:
            if last_time == None:
                last_time = v['time']
                latest_version = v['version']
                continue
            # eg: "2025-04-28T14:35:15+00:00"
            current_time = datetime.fromisoformat(v['time'].replace("Z", "+00:00"))
            if datetime.fromisoformat(last_time.replace("Z", "+00:00")) < current_time:
                last_time = str(v['time'])
                latest_version = str(v['version'])
    
    return latest_version
            


def get_packagist_archive_url(pkg_name, version):
    response = requests.get(f"https://repo.packagist.org/p2/{pkg_name}.json")
    response.raise_for_status()
    data = response.json()
    
    for versions in data['packages'].keys():
        for v in data['packages'][versions]:
            if v['version'] == version:
                return v['dist']['url']
            
def get_packagist_archive_filename(pkgName, version, _ :str ):
    pkg = pkgName.split("/")
    return ''.join([pkg[0], '-', pkg[1], '-', version, '.zip'])



packagist_pkg_manager = PkgManager(
    ecosystem=Ecosystem.PACKAGIST,
    latest_version_func=get_packagist_latest,
    archive_url_func=get_packagist_archive_url,
    archive_filename_func=get_packagist_archive_filename,
    extract_archive_func=Extracter.extract_packagist_file,
)