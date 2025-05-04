import os
import tarfile
import gzip
import shutil
import requests
from urllib.parse import urlparse
import zipfile

class Extracter:
    @staticmethod 
    def extract_archive_file(archive_path, output_dir):
        """
        Extracts a .tar.gz / .tgz file located at archive_path,
        using output_dir as the root of the extracted files.
        """
        try:
            with gzip.open(archive_path, 'rb') as gz_file:
                return Extracter.extract_tar(gz_file, output_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to extract archive: {e}")

    @staticmethod
    def extract_tar(tar_stream, output_dir):
        """
        Extracts the contents of the given tar archive stream,
        using output_dir as the root of the extracted files.
        """
        if not output_dir:
            raise ValueError("output_dir is empty")

        try:
            with tarfile.open(fileobj=tar_stream, mode="r:*") as tar:
                for member in tar.getmembers():
                    output_path = os.path.join(output_dir, member.name)

                    # Check for ZipSlip vulnerability
                    # if not os.path.commonpath([output_dir, output_path]).startswith(output_dir):
                    #     raise RuntimeError(f"Archive path escapes output dir: {member.name}")

                    if member.isdir():
                        # Create directory with appropriate permissions
                        os.makedirs(output_path, exist_ok=True)
                    elif member.isfile():
                        # Ensure parent directories exist
                        parent_dir = os.path.dirname(output_path)
                        os.makedirs(parent_dir, exist_ok=True)

                        # Extract file
                        with open(output_path, 'wb') as extracted_file:
                            extracted_file.write(tar.extractfile(member).read())
                    else:
                        raise RuntimeError(f"{member.name} has unknown type {member.type}")

        except Exception as e:
            raise RuntimeError(f"Failed to extract tar archive: {e}")

    @staticmethod
    def extract_gem(gem_path, output_dir):
        """
        Extracts a RubyGem package (.gem file) to retrieve only the source code
        and moves it to the output folder.

        Gem files are uncompressed tar archives. This function extracts the
        `data.tar.gz` file from the .gem archive and then extracts its contents.
        """
        if not os.path.exists(gem_path):
            raise FileNotFoundError(f"Gem file not found: {gem_path}")

        if not output_dir:
            raise ValueError("Output directory is not specified")

        try:
            # Create a temporary directory to extract the .gem file
            temp_dir = os.path.join(output_dir, "temp_extraction")
            os.makedirs(temp_dir, exist_ok=True)

            # Extract the .gem file
            with tarfile.open(gem_path, "r:*") as gem_tar:
                gem_tar.extractall(temp_dir)

            # Locate the data.tar.gz file
            data_tar_gz_path = os.path.join(temp_dir, "data.tar.gz")
            if not os.path.exists(data_tar_gz_path):
                raise RuntimeError("data.tar.gz not found in the .gem file")

            # Extract the data.tar.gz file
            with gzip.open(data_tar_gz_path, "rb") as data_tar_gz:
                with tarfile.open(fileobj=data_tar_gz, mode="r:*") as data_tar:
                    data_tar.extractall(output_dir)

        except Exception as e:
            raise RuntimeError(f"Failed to extract gem file: {e}")

        finally:
            # Force cleanup of the temporary directory
            def handle_remove_readonly(func, path, exc_info):
                os.chmod(path, 0o777)  # Make the file writable
                func(path)

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)




    @staticmethod
    def extract_packagist_file(archive_path, output_dir):
        """
        Extracts a Packagist package (.zip file) to the specified output directory.
        """
        if not archive_path.endswith('.zip'):
            raise RuntimeError(f"Invalid file format: {archive_path} is not a .zip file")

        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive file not found: {archive_path}")

        if not output_dir:
            raise ValueError("Output directory is not specified")

        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Extract all files to the output directory
                zip_ref.extractall(output_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to extract Packagist file: {e}")
        
    @staticmethod
    def extract_jar_file(jar_path, output_dir):
        """
        Extracts the contents of a .jar file to the specified output directory.
        """
        if not jar_path.endswith('.jar'):
            raise RuntimeError(f"Invalid file format: {jar_path} is not a .jar file")

        if not os.path.exists(jar_path):
            raise FileNotFoundError(f"JAR file not found: {jar_path}")

        if not output_dir:
            raise ValueError("Output directory is not specified")

        try:
            with zipfile.ZipFile(jar_path, 'r') as jar_file:
                # Extract all files to the output directory
                jar_file.extractall(output_dir)
                print(f"Extracted .jar file to: {output_dir}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract JAR file: {e}")