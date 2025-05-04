from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from typing import List, Optional

class PackageNotFoundException(Exception):
    """
    Abstract exception raised when a package cannot be found.
    """
    pass

class PackageRelease(ABC):
    """
    Abstract class representing a package release.
    """
    
    def get_package(self) -> AbstractPackage:
        """
        Get the package owner of this release.

        Returns:
            AbstractPackage: The package owner of this release.
        """
        pass

    
    def get_download_url(self) -> str:
        """
        Get the release download URL.

        Returns:
            str: The release download URL.
        """
        pass

    
    def get_release_file_name(self) -> str:
        """
        Get the release file name.

        Returns:
            str: The release file name.
        """
        pass

    
    def get_release_file_type(self) -> str:
        """
        Get the release file type (e.g., filename extension).

        Returns:
            str: The release file type.
        """
        pass

class AbstractPackage(ABC):


 




  
  def getName(self) -> str:
    """
      Get the package name

        Return (str):
          the package name
    """
    pass

  
  def getVersion(self):
    """
      Get the package version

        Return (str):
          the package version
    """
    pass

  
  def getRelaeses(self) -> list[PackageRelease]:
    """
      Get all the available releases for the package

        Return (list):
          the package name
    """
    pass


  def __loadReleases(self) -> None:
    """
      Extract from the package metadata the list of available release files and store them in the self.releases variable
    """
    pass

  
  def getGitRepositoryUrl(self) -> str:
    """
      Get the package git repository url, if found

        Return (str):
          the package git repository url if found, otherwise None
    """
    pass


  def __loadSourcesRepository(self):
    """
      Scan the package metadata searching for a source git repository and stor the value in "self.git_repository_url"
    """
    pass
    

  def __str__(self):
    return "AbstractPackage"


class PackageRelease(PackageRelease):
    """
        Class that represent a npmthon package release
    """

    def __init__(self, package:AbstractPackage ,url:str, package_type:str = None) -> None:
        """
        Constructor of the npmPackageRelease class

            Parameters:
            npmpackage(npmPackage): The package owner of this release
            url(str): The url of the release file
            package_type(str): The type of the release file (wheel, source, egg, etc...)
        """
        pass
    
    
    def getPackage(self) -> AbstractPackage:
        """
        Get the package owner of this release

            Return (npmPackage):
            the package owner of this release
        """
        pass

    
    def getDownloadUrl(self) -> str:
        """
        Get the relase download url

            Return (str):
            the relase download url
        """
        pass

    
    def getReleaseFileName(self) -> str:
        """
        Get the relase file name

            Return (str):
            the relase file name
        """
        pass

    
    def getReleaseFileType(self) -> str:
        """
        Get the relase file type (In practice the filename extension)

            Return (str):
            the the relase file type 
        """
        pass