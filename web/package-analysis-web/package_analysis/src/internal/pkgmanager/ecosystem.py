import os
import requests
from urllib.parse import urlparse
from enum import Enum

from ..pkg import programkind

class Ecosystem(str, Enum):
    NONE = ""
    CRATES_IO = "crates.io"
    NPM = "npm"
    PACKAGIST = "packagist"
    PYPI = "pypi"
    RUBYGEMS = "rubygems"
    MAVEN = "maven"


class PkgManager:
    def __init__(self, ecosystem: Ecosystem, latest_version_func, archive_url_func, archive_filename_func, extract_archive_func=None):
        self.ecosystem = ecosystem
        self.latest_version_func = latest_version_func
        self.archive_url_func = archive_url_func
        self.archive_filename_func = archive_filename_func
        self.extract_archive_func = extract_archive_func
        self.archive_filename = None

    def get_base_filename(self):
        basename = self.archive_filename
        ext = programkind.get_ext(basename)
        return str(basename).replace(ext, '')
        

    def latest(self, name):
        name = self.normalize_pkg_name(name)
        version = self.latest_version_func(name)
        return Pkg(name, version, self)

    def package(self, name, version):
        return Pkg(self.normalize_pkg_name(name), version, self)

    def download_archive(self, name, version, directory="/tmp/"):
        download_url = self.archive_url_func(name, version)
        if not download_url:
            raise ValueError(f"Archive URL not found for package {name} @ {version}")

        base_filename = self.archive_filename_func(name, version, download_url)
        self.archive_filename = base_filename
        if not base_filename:
            raise ValueError("Base filename for archive is empty")

        dest_path = os.path.join(directory, base_filename)
        self.download_to_path(dest_path, download_url)
        return dest_path

    def extract_archive(self, archive_path, output_dir):
        if self.extract_archive_func:
            return self.extract_archive_func(archive_path, output_dir), output_dir
        raise NotImplementedError(f"Archive extraction not implemented for {self.ecosystem}")

    @staticmethod
    def normalize_pkg_name(pkg):
        return pkg.lower()

    @staticmethod
    def download_to_path(path, url):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    @staticmethod
    def default_archive_filename(_, __, download_url):
        """
        Returns a naive default choice of filename from a download URL
        by simply returning everything after the final slash in the URL.
        """
        return os.path.basename(urlparse(download_url).path)



class Pkg:
    def __init__(self, name, version, manager):
        self.name = name
        self.version = version
        self.manager = manager

    def __str__(self):
        return f"{self.name}:{self.version} ({self.manager.ecosystem})"
