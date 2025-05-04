from __future__ import annotations
import logging
import os,urllib
import requests
import json
from urllib.parse import quote
from lxml import html

from lastpymile.utils import Utils
from .abstractpackage import AbstractPackage, PackageNotFoundException, PackageRelease
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from py2src.py2src.url_finder import   URLFinder

class NpmPackage(AbstractPackage):
  """
    Class that represent a npmthon package from npm.org
  """

  # __RELEASE_TYPE_WHEEL="wheel"
  # __RELEASE_TYPE_SOURCE="source"
  # __RELEASE_TYPE_EGG="egg"
  # __RELEASE_TYPE_UNKNOWN="unknown"

  __npm_URL="https://registry.npmjs.org"

  __logger=logging.getLogger("lastpymile.npmPackage")

 
  @staticmethod
  def searchPackage(package_name:str, package_version:str=None, checked:bool=False) -> NpmPackage:
    """
      Static method to create a npmPackage from its name and an optional version

        Parameters:
          package_name(str): The name of the package
          package_version(str): The version of the package. May be None, in that case the latest version is retrieved
          checked(bool): If True no exceptions are rasied if the pacakge cannot be found and None is returned. Default is False

        Return (npmPackage):
          The npmPackage object

        Raise (npmPackageNotFoundException): If the package couldn't be found
    """
    safe_name=quote(package_name, safe='')
    safe_ver=quote(package_version, safe='') if package_version is not None else None
    # safe_ver = None
    partial_url="{}".format(safe_name) if package_version is None else "{}/{}".format(safe_name,safe_ver)
    url="{}/{}".format(NpmPackage.__npm_URL,partial_url)
    NpmPackage.__logger.debug("Downloading package '{}' data from {}".format(package_name,url))
    try:
      return NpmPackage(json.loads(Utils.getUrlContent(url)))
      
    except Exception as e:
      if checked==True:
        return None
      print("Error: ", e)
      raise NpmPackageNotFoundException(safe_name,safe_ver) from e
      

  def __init__(self,package_data) -> None: 
    self.package_data=package_data
    self.name=self.package_data["name"]
    self.version=self.package_data["dist-tags"]["latest"]
    self.releases=None
    self.git_repository_url=None

  def getName(self) -> str:
    """
      Get the package name

        Return (str):
          the package name
    """
    return self.name

  def getVersion(self):
    """
      Get the package version

        Return (str):
          the package version
    """
    return self.version

  def getRelaeses(self) -> list[NpmPackageRelease]:
    """
      Get all the available releases for the package

        Return (list):
          the package name
    """
    if self.releases==None:
      self.__loadReleases()
    return self.releases

  def __loadReleases(self) -> None:
    """
      Extract from the package metadata the list of available release files and store them in the self.releases variable
    """
    self.releases=[]
    for version in self.package_data["versions"].keys():
      release=self.package_data["versions"][version]
      if "dist" in release and version == self.version:
        release_url = release.get("dist", {}).get("tarball", None)
        # default package type is tarball
        package_type = "tarball"
        if release_url:
            self.releases.append(NpmPackageRelease(self, release_url, package_type))

  def getGitRepositoryUrl(self) -> str:
    """
      Get the package git repository url, if found

        Return (str):
          the package git repository url if found, otherwise None
    """
    if self.git_repository_url==None:
      self.__loadSourcesRepository()
    return self.git_repository_url

  def __loadSourcesRepository(self):
    """
      Scan the package metadata searching for a source git repository and stor the value in "self.git_repository_url"
    """
    github_link=None
    urls=self.package_data["versions"][self.version].get("repository", {}).get("url", None)

    if urls is not None:
      if isinstance(urls, list):
        for url in urls:
          if "github.com" in url:
            github_link=url
            break
      else:
        if "github.com" in urls:
          github_link=urls

    github_link = URLFinder.real_github_url(github_link) if github_link is not None else None
    self.git_repository_url=github_link
    
  def __str__(self):
    return "npmPackage[name:{}, version:{}, github:{}, release:({}){}]".format(self.name,self.version,self.githubPageLink,self.releaseLink[1],self.releaseLink[0])


class NpmPackageRelease(PackageRelease):
  """
    Class that represent a npmthon package release
  """

  def __init__(self, npmpackage:NpmPackage ,url:str, package_type:str = None) -> None:
    """
      Constructor of the npmPackageRelease class

        Parameters:
          npmpackage(npmPackage): The package owner of this release
          url(str): The url of the release file
          package_type(str): The type of the release file (wheel, source, egg, etc...)
    """
    self.npmpackage=npmpackage
    self.url=url

  def getnpmPackage(self) -> NpmPackage:
    """
      Get the package owner of this release

        Return (npmPackage):
          the package owner of this release
    """
    self.npmpackage

  def getDownloadUrl(self) -> str:
    """
      Get the relase download url

        Return (str):
          the relase download url
    """
    return self.url

  def getReleaseFileName(self) -> str:
    """
      Get the relase file name

        Return (str):
          the relase file name
    """
    return os.path.basename(urllib.parse.urlparse(self.url).path)

  def getReleaseFileType(self) -> str:
    """
      Get the relase file type (In practice the filename extension)

        Return (str):
          the the relase file type 
    """
    return self.getReleaseFileName().split(".")[-1]


##################################
##  EXCEPTIONS
##################################

class NpmPackageNotFoundException(PackageNotFoundException):
  """
    Exception raised when a package cannot be found on npm.org
  """

  def __init__(self, package_name:str, package_version:str=None) -> None:
    """
      Constructor of the npmPackageNotFoundException class

        Parameters:
          package_name(str): The name of the package that couldn't be found
          package_version(str): The version of the package that couldn't be found. May be None if not specified
    """
    self.package_name=package_name
    self.package_version=package_version
    if package_name is None:            
      super().__init__("npm package '{}' not found".format(package_name))
    else:
      super().__init__("npm package '{}' version '{}' not found".format(package_name,package_version))