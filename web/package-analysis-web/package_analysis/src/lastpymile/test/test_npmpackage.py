import pytest
from unittest.mock import patch, MagicMock
from lastpymile.pkgmanager.npmpackage import NpmPackage, NpmPackageRelease, NpmPackageNotFoundException
import json

@pytest.fixture
def mock_package_data():
    try:
        with open("data/tokio.json", "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError("The file 'data/tokio.json' was not found. Please check the path.")

@pytest.fixture
def npm_package(mock_package_data):
    return NpmPackage(mock_package_data)

def test_search_package_success(mock_package_data):
    # with patch("lastpymile.utils.Utils.getUrlContent", return_value=json.dumps(mock_package_data)):
    package = NpmPackage.searchPackage("tokio")
    # print type of class of package
    # get type of class of package
    assert isinstance(package, NpmPackage)
    assert package.getName() == "tokio"
    assert package.getVersion() == "0.1.2"

def test_search_package_not_found():
    with patch("lastpymile.utils.Utils.getUrlContent", side_effect=Exception("404 Not Found")):
        with pytest.raises(NpmPackageNotFoundException):
            NpmPackage.searchPackage("nonexistent-package")

def test_search_package_checked():
    with patch("lastpymile.utils.Utils.getUrlContent", side_effect=Exception("404 Not Found")):
        package = NpmPackage.searchPackage("nonexistent-package", checked=True)
        assert package is None

def test_get_name(npm_package):
    assert npm_package.getName() == "tokio"

def test_get_version(npm_package):
    assert npm_package.getVersion() == "0.1.2"

def test_get_releases(npm_package):
    releases = npm_package.getRelaeses()
    assert len(releases) > 1 
    assert releases[-1].getDownloadUrl() == "https://registry.npmjs.org/tokio/-/tokio-0.1.2.tgz"
    assert releases[-1].getReleaseFileName() == "tokio-0.1.2.tgz"
    assert releases[-1].getReleaseFileType() == "tgz"

def test_get_git_repository_url(npm_package):
    assert npm_package.getGitRepositoryUrl() == "https://github.com/egoist/tokio.git"




