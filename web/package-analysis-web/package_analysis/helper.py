import requests
import tempfile
import subprocess
import json
import os
import time
import re
import git
from pathlib import Path
from collections import defaultdict
from functools import lru_cache


from bs4 import BeautifulSoup
from datetime import datetime
import logging
import shutil
from collections import Counter
from .src.utils import log_function_output

from .src.py2src.py2src.url_finder import  GetFinalURL, URLFinder
from .src.internal.pkgmanager.package import pkg
from .src.lastpymile.lastpymile.utils import Utils


current_path = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_path, 'logs', 'helper.log')
# crate an empty logfile and overwrite the old one
if os.path.exists(log_file):
    os.remove(log_file)
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logger = log_function_output(file_level=logging.DEBUG, console_level=logging.CRITICAL,
                              log_filepath=log_file)



class Helper:

    @staticmethod
    def find_root_path():
                # This command to search the analysis script path in wsl environment
        command_search_analysis_script = "wsl pwd"

        if Helper.is_windows_environment():
            command_search_analysis_script = "wsl pwd"
        else:
            command_search_analysis_script = "pwd"
        output_path = subprocess.run(command_search_analysis_script,
                                      shell=True, check=True, capture_output=True,
                                        text=True).stdout.strip()
        # back two directories to get the root directory of Pack-a-mal
        output_list = output_path.split("/")[:-2]
        root_path = "/".join(output_list)
        return root_path

    @staticmethod
    def find_script_path():
        ''' Find scripts/analysis.sh path in the root directory of Pack-a-mal'''
        root_path = Helper.find_root_path()

        # script path is the root directory of Pack-a-mal + scripts/run_analysis.sh
        script_path = root_path + "/scripts/run_analysis.sh"
        return script_path


    @staticmethod
    def is_windows_environment():
        return os.name == 'nt'
    
    @staticmethod
    @lru_cache(maxsize=1) 
    def fetch_package_list():
        root_path = Helper.find_root_path()
        INDEX_DIR = os.path.join(root_path, 'web', 'crates.io-index')
        if not os.path.exists(INDEX_DIR):
            git.Repo.clone_from('https://github.com/rust-lang/crates.io-index.git', INDEX_DIR)

        def get_all_crates(index_dir):
            crates = defaultdict(list)
            for root, _, files in os.walk(index_dir):
                if '.git' in root: 
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    if file in ['README.md', 'config.json']:
                        continue
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:

                            try:
                                crate_info = json.loads(line)
                                crates[crate_info['name']].append(crate_info['vers'])
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON in file {file_path}: {e} line {line}")
                            except KeyError as e:
                                print(f"Missing key in JSON in file {file_path}: {e} line {line}")
            return crates

        crates_list = get_all_crates(INDEX_DIR)
        print(f"Total number of crates: {len(crates_list.keys())}")
        return crates_list
    
    @staticmethod
    def search_apk(package_name):
        raw_package_list = Helper.fetch_package_list()
        package_repo_names = [pkg.replace('.apk', '') for pkg in raw_package_list]

        package_repo_names = sorted(package_repo_names, key=lambda x: (x, len(x)))

        for package in package_repo_names:
            if package.startswith(package_name):
                return Helper.download_apk(package)
        
        raise ValueError(f'apk {package_name} not found in wolfi registry.')

    @staticmethod     
    def download_apk(package_repo_name):
        arch = "x86_64"
        package_url = f"https://packages.wolfi.dev/os/{arch}/{package_repo_name}.apk"
        # download the apk and save to temporary location and return the location of the apk
        try:
            response = requests.get(package_url)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as temp_file:
                temp_file.write(response.content)
                return temp_file.name
            print(f"Failed to download APK: {e}")
            raise
        except IOError as e:
            print(f"Failed to write APK to file: {e}")
            raise

    @staticmethod
    def get_latest_package_version(package_name, ecosystem):

        url = f"https://api.deps.dev/v3/systems/{ecosystem}/packages/{package_name}"
        print(f"Fetching latest version for package: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()


            versions = data.get('versions', [])
            latest_version = None
            for version in versions:
                ts = version.get("publishedAt")
                if ts != None:
                    ts = ts.replace("Z", "+00:00")
                    curent_date = datetime.fromisoformat(ts)
                    if latest_version == None:
                        latest_version = version
                    elif curent_date > datetime.fromisoformat(latest_version.get("publishedAt").replace("Z", "+00:00")):
                        latest_version = version
            return latest_version['versionKey']['version']
        else:
            print(f"Failed to fetch data for package: {package_name}")
            return None
        
    @staticmethod
    def get_source_url(package_name, ecosystem):

        '''get source url of the package from deps.dev'''

        latest_version = Helper.get_latest_package_version(package_name, ecosystem)
        print(f"Latest version for package {package_name}: {latest_version}")
        if latest_version == None:
            print(f"Failed to get latest version for package: {package_name}")
            return None
        
        url = f"https://api.deps.dev/v3alpha/systems/{ecosystem}/packages/{package_name}/versions/{latest_version}"
        print(f"Fetching source url for package: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for link in data['links']:
                if link['label'] == 'SOURCE_REPO':
                    return link['url']
        else:
            print(f"Failed to fetch data for package: {package_name}")
            return None
        
    @staticmethod
    def get_maven_packages():

        '''
        get maven packages from maven_packages.json file.
        data {
        "groupID: {"artifactID": ["version1", "version2"]}
        '''
        def combine_json_files(directory):
            """Combines multiple JSON files in a directory into a single JSON file.

            Args:
                directory: The directory containing the JSON files.
            """
            combined_data = {}
            for filename in os.listdir(directory):
                if filename.endswith(".json"):
                    filepath = os.path.join(directory, filename)
                    with open(filepath, 'r') as f:
                        try:
                            data = json.load(f)
                            combined_data.update(data)
                        except json.JSONDecodeError:
                            print(f"Skipping invalid JSON file: {filename}")

            return combined_data
        
        current_path = os.path.dirname(os.path.abspath(__file__))
        data = combine_json_files(os.path.join(current_path, 'resources', 'maven_package_names'))

        return data

        
        
    @staticmethod       
    def get_rust_packages():
        current_path = os.path.dirname(os.path.abspath(__file__))
        rust_packages_path = os.path.join(current_path, 'resources','crates_packages.json')
        if os.path.exists(rust_packages_path):
            with open(rust_packages_path, 'r') as file:
                packages = json.load(file)

            return packages
        
        os.makedirs(os.path.dirname(rust_packages_path), exist_ok=True)
        packages = Helper.fetch_package_list()
        with open(rust_packages_path, 'w') as file:
            json.dump(packages, file)
            
        packages =  Helper.fetch_package_list()
        return packages 
    
    @staticmethod
    def get_pypi_packages():
        import csv
        curent_path = os.path.dirname(os.path.abspath(__file__))
        pypi_packages_path = os.path.join(curent_path, 'resources', 'pypi_package_names.csv')
        if os.path.exists(pypi_packages_path):
            with open(pypi_packages_path, 'r') as file:
                reader = csv.reader(file)
                # skip the header
                next(reader)
                packages = [row[0] for row in reader]

            return {"packages": list(packages)}
        
        url = "https://pypi.org/simple/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        package_names = [a.text for a in soup.find_all('a')]

        with open(pypi_packages_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Package Name"])
            for package in package_names:
                writer.writerow([package])
        
        return {"packages": package_names}
    
    @staticmethod
    def get_rubygems_packages():
        import csv
        current_path = os.path.dirname(os.path.abspath(__file__))
        rubygems_packages_path = os.path.join(current_path, 'resources', 'rubygems_package_names.csv')
        if os.path.exists(rubygems_packages_path):
            with open(rubygems_packages_path, 'r') as file:
                reader = csv.reader(file)
                # skip the header
                next(reader)
                packages = [row[0] for row in reader]


            return {"packages": list(packages)}

        url = 'https://rubygems.org/names'

        response = requests.get(url)
        response.raise_for_status()  # Ensure request was successful

        gem_names = response.text.splitlines()

        with open(rubygems_packages_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Package Name"])
            for gem in gem_names:
                writer.writerow([gem])
        
        return {"packages": gem_names}
        

    @staticmethod
    def get_packagist_packages():
        # https://packagist.org/packages/list.json
        current_path = os.path.dirname(os.path.abspath(__file__))
        packagist_packages_path = os.path.join(current_path, 'resources', 'packagist_package_names.json')
        if os.path.exists(packagist_packages_path):
            with open(packagist_packages_path, 'r') as file:
                packages = json.load(file)
            return {"packages": packages.get('packageNames', [])}
        
        url_packagist_names = 'https://packagist.org/packages/list.json'
        response = requests.get(url_packagist_names) 
        if response.status_code == 200:
            data = response.json()
            with open(packagist_packages_path, 'w') as file:
                json.dump(data, file)
            return {"packages": data.get('packageNames', [])}
        else:
            raise ValueError(f"Failed to fetch packagist package names: {response.status_code}")

    @staticmethod
    def get_npm_packages():
        # https://github.com/nice-registry/all-the-package-names/tree/master
        current_path = os.path.dirname(os.path.abspath(__file__))
        npm_packages_path = os.path.join(current_path, 'resources', 'npm_package_names.json')
        if os.path.exists(npm_packages_path):
            with open(npm_packages_path, 'r') as file:
                packages = json.load(file)
            return {"packages": packages}
        
        url_npm_names = 'https://github.com/nice-registry/all-the-package-names/raw/refs/heads/master/names.json'
        response = requests.get(url_npm_names) 
        if response.status_code == 200:
            data = response.json()
            with open(npm_packages_path, 'w') as file:
                json.dump(data, file)
            return {"packages": data}
        else:
            raise ValueError(f"Failed to fetch npm package names: {response.status_code}")  
    
    @staticmethod
    def handle_uploaded_file(file_path, package_name, package_version, ecosystem):
        # /media/listing-0_UwODAKy.1-r0.apk

        local_path = Helper.find_root_path() + '/web/package-analysis-web' + file_path
        report = Helper.run_package_analysis(package_name, package_version, ecosystem, local_path=local_path)
        # delete local file after analysis
        if os.path.exists(local_path):
            os.remove(local_path)
        return report

    @staticmethod
    def run_py2src(package_name, package_version, ecosystem):

      url_data = GetFinalURL(package_name).get_final_url()
      github_url = url_data[0]
      print("Package name: ", package_name, "Github URL: ", github_url)
      return [github_url]
          



    @staticmethod
    def run_oss_find_source(package_name, package_version, ecosystem):
        '''
            find source code using oss-gadget
        '''
        
        ecosystem = Helper.transfer_ecosystem(ecosystem)
        folder_path = os.path.join(tempfile.gettempdir(), "oss-find-source")
        file_save_name = f"{package_name}.sarif"
        dst = os.path.join(folder_path, file_save_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        

        # executable = r"oss-find-source"
        # Helper.check_executable_in_path(executable)
        # command = f'{executable} -o "{dst}" --format sarifv2 pkg:{ecosystem}/{package_name}@{package_version}'

        command = [
            "docker", "run", "--rm",
            "-v", f"{folder_path}:/tmp/oss-find-source",  # Mount the folder path to the same path inside the container
            "pakaremon/ossgadget:latest", 
            "bash",
            "-c",
            f'"mkdir -p /tmp/oss-find-source && oss-find-source pkg:{ecosystem}/{package_name} --format sarifv2 -o /tmp/oss-find-source/{file_save_name}"'
        ]
        print(f"Output saved to {dst} after running the command: {' '.join(command)}")
        def parse_sarif(sarif_file):
            try:
                with open(sarif_file, 'r') as f:
                    data = json.load(f)
                    url_sources = []
                    for candidate in data['runs'][0]['results']:
                        if candidate:
                            location = candidate.get('locations', [])[0]
                            if location:
                                address = location.get('physicalLocation', {}).get('address', {})
                            if 'fullyQualifiedName' in address:
                                url_sources.append(address['fullyQualifiedName'])
                            message = candidate.get('message', {}).get('text')
                            if message:
                                url_sources.append(message)


                    return url_sources
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return []
            except FileNotFoundError as e:
                print(f"File not found: {e}")
                return []
            
        try:
            # if os.path.exists(dst):
            #     url_sources = parse_sarif(dst)
            #     return url_sources
            
            results = subprocess.run(' '.join(command), shell=True, check=True, capture_output=True, text=True)
            print(results.stdout)
            print(results.stderr)
            print(f"Command executed successfully: {command}")

            url_sources = parse_sarif(dst)
            print(f"URL sources found: {url_sources}")

            additional_urls = Helper.get_source_url(package_name, ecosystem)
            url_sources.append(additional_urls)
            print(f"Additional URL sources found: {additional_urls}")
            url_sources = list(set(url_sources))  # Remove duplicates
            # remove None values
            url_sources = [url for url in url_sources if url is not None]
            return url_sources
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")
            raise

        

        

        


    @staticmethod
    def transfer_ecosystem(ecosystem):
        if ecosystem == "crates.io":
            return "cargo"
        elif ecosystem == "pypi":
            return "pypi"
        elif ecosystem == "npm":
            return "npm"
        elif ecosystem == "rubygems":
            return "gem"
        elif ecosystem == "packagist":
            return "composer"
        elif ecosystem == "maven":
            return "maven"
        else:
            raise ValueError(f"Unknown ecosystem: {ecosystem}")

    def check_executable_in_path(executable_name: str) -> str:
        """
        Check if an executable exists in the system PATH using `which`.
        Returns the full path to the executable if found.
        Raises FileNotFoundError if not found.
        """
        try:
            result = subprocess.run(
                ["which", executable_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            path = result.stdout.strip()
            if path:
                print(f"✅ '{executable_name}' found at: {path}")
                return path
        except subprocess.CalledProcessError:
            pass

        raise FileNotFoundError(f"❌ '{executable_name}' not found in PATH.")

    @staticmethod
    def run_oss_squats(package_name, package_version, ecosystem):


        print(f"find typosquats for package: {package_name}, version: {package_version}, ecosystem: {ecosystem}")
        ecosystem = Helper.transfer_ecosystem(ecosystem)
        folder_path = os.path.join(tempfile.gettempdir(), "oss-find-squats")
        file_save_name = f"{package_name}_{ecosystem}.sarif"
        dst = os.path.join(folder_path, file_save_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # executable = r"oss-find-squats"
        # Helper.check_executable_in_path(executable)
        # command = f'{executable} -o "{dst}" --format sarifv2 pkg:{ecosystem}/{package_name}@{package_version}'

        command = [
            "docker", "run", "--rm",
            "-v", f"{folder_path}:/tmp/oss-find-squats",  # Mount the folder path to the same path inside the container
            "pakaremon/ossgadget:latest", 
            "bash",
            "-c",
            f'"mkdir -p /tmp/oss-find-squats && oss-find-squats pkg:{ecosystem}/{package_name} --format sarifv2 -o /tmp/oss-find-squats/{file_save_name}"'
        ]
        print(f"Output saved to {dst} after running the command: {' '.join(command)}")

        def parse_sarif(sarif_file):
            try:
                with open(os.path.join(sarif_file), 'r') as f:
                    data = json.load(f)
                    package_names = []
                    for candidate in data['runs'][0]['results']:
                        if candidate['message']['text'].startswith('Potential Squat candidate'):
                            package_names.append(candidate['locations'][0]['physicalLocation']['address']['name'].split('/')[-1])
                        
                    return package_names
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return []
            except FileNotFoundError as e:
                print(f"File not found: {e}")
                return []
                
        try:
            if os.path.exists(dst):
                package_names = parse_sarif(dst)
                return package_names

            print("Command: ", command) 
            result = subprocess.run(' '.join(command), shell=True, check=True, capture_output=True, text=True, timeout=600)
            print(f"Command executed successfully: {command}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            package_names = parse_sarif(dst)  
            return package_names

        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")
            raise #always raise the error to the caller

    @staticmethod
    def run_bandit4mal(package_name, package_version, ecosystem):

        FILE_TEXT_EXTENSION = [
            '.txt',    # Plain text file
            '.md',     # Markdown file
            '.rtf',    # Rich Text Format
            '.csv',    # Comma-Separated Values
            '.log',    # Log file
            '.xml',    # XML file
            '.yaml',   # YAML Ain't Markup Language
            '.yml',    # YAML Ain't Markup Language
            '.ini',    # Initialization file
            '.conf',   # Configuration file
            '.cfg',    # Configuration file
            '.sql',    # SQL file
            '.tex',    # LaTeX file
            '.html',   # Hypertext Markup Language
            '.htm',    # Hypertext Markup Language
            '.srt',    # SubRip Subtitle
        ]



        def parse_bandit_results(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results = []
                    number_of_alert = Counter()
                    for result in data.get('results', []):
                        file_path = result.get('filename', 'Unknown')
                        if not file_path.endswith(tuple(FILE_TEXT_EXTENSION)):
                                if result.get('issue_severity', '').lower() in ['high', 'critical']:
                                    number_of_alert[file_path] += 1
                    
                    for file, count in number_of_alert.most_common():
                        results.append({
                            'package': {
                                'name': package_name,
                                'version': package_version,
                                'ecosystem': ecosystem
                            },
                            'file': file,
                            'number_of_alerts': count,
                        })
                    
                    return results
                        
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error processing file {file_path}: {e}")
                return []
        # TODO 0 build ecosystem pkg manager: ✅ 
            # 0.1 find latest version
            # 0.2 find url archieve
            # 0.3 download url archieve
            # 0.4 extract archieve file

        pkg_manager = pkg(package_name, package_version, ecosystem).manager
        # Check version exists
        specific_package = pkg_manager.package(package_name, package_version)
        print(f"Specific package: {specific_package}")
        download_directory = os.path.join(tempfile.gettempdir(), 'bandit4mal_downloaded')
        os.makedirs(download_directory, exist_ok=True)
        archive_path = pkg_manager.download_archive(package_name, package_version, download_directory)
        print(f"Downloaded archive to: {archive_path}")
        extract_directory = os.path.join(tempfile.gettempdir(), 'bandit4mal_extracted', pkg_manager.get_base_filename())
        _ , extracted_dir = pkg_manager.extract_archive(archive_path, output_dir=extract_directory)
        print(f"Extracted archive to: {extracted_dir}")

        # TODO run bandit4mal
        root_path = Helper.find_root_path()
        # web\package-analysis-web\venv\bin\bandit
        venv_bandit_path = root_path + "/web/package-analysis-web/venv/bin/bandit"
        json_folder = os.path.join(tempfile.gettempdir(), 'bandit4mal_json_results')
        os.makedirs(json_folder, exist_ok=True)
        output_file = os.path.join(json_folder, f"{pkg_manager.get_base_filename()}.json")
        command = [venv_bandit_path, '-r', extracted_dir, '-f', 'json', '-o', output_file]
        print(' '.join(command))

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command executed successfully: {' '.join(command)}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")


        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")
            # raise #always raise the error to the caller
        
        # report = parse_bandit_results(output_file)

        try:
            with open(output_file, "r", encoding="utf-8") as json_file:
                report = json.load(json_file)
        except FileNotFoundError:
            raise

        Utils.rmtree(extract_directory)
        Utils.rmtree(download_directory)
        return report



    @staticmethod
    def run_lastpymile(package_name, package_version=None, ecosystem='pypi'):
        '''
        Identify discrepancies between the source code repositories and the published package artifacts in PyPI.
        By integrating find modified files and bandit tools, reduce the false positive rate of the results.
        '''

        # files = ['Colorama.json', 'requests-mock.json', 'six.json']
        # # for testing purpose, use the local json file
        # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'lastpymile', 'tmp', files[2]), 'r') as f:
        #     data = json.load(f)
        #     return data
         

        current_path = os.path.dirname(os.path.abspath(__file__))
        lastpymile_path_script = os.path.join(current_path, 'src', 'lastpymile', 'lastpymile.py')

        save_path = os.path.join(tempfile.gettempdir(), "lastpymile")
        os.makedirs(save_path, exist_ok=True)

        # package version is optional, run the command
        # if package_version:
        #     command = f"python {lastpymile_path_script} {package_name}:{package_version} -f {save_path}/{package_name}.json"
        # else:
        
        root_path = Helper.find_root_path()
        python_venv_path = os.path.join(root_path, 'web', 'package-analysis-web', 'venv', 'bin', 'python')
        command = f"{python_venv_path} {lastpymile_path_script}  {package_name} -e {ecosystem} -f {save_path}/{package_name}.json"
        
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command executed successfully: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        


        # read the json file and return the data
        try:
            with open(f"{save_path}/{package_name}.json", 'r') as f:
                data = json.load(f)

                return data
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e}")
            

        

        
        



        
 
    @staticmethod
    def run_package_analysis(package_name, package_version, ecosystem, local_path=None):
        print(f" Run package-analysis: Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
        # ./scripts/run_analysis.sh -ecosystem Rust -package littlest -version littlest.0.0.0  -local /path/fijiwashere12323-0.0.0-r0.apk -sandbox-image 'wolfi-apk/dynamic-analysis'   -analysis-command 'analyze_wolfi_apk.py' -mode dynamic -nopull 
        # run the script with the package name, version, ecosystem and the path to the apk
        # the script should return the results of the analysis
        # for now, just print the command to the console

        script_path = Helper.find_script_path()
        image_name = "docker.io/pakaremon/dynamic-analysis:latest"
        try:
            # Check if the image exists locally
            subprocess.run(f"docker image inspect {image_name}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            image_exists = True
        except subprocess.CalledProcessError:
            image_exists = False

        if local_path:
            if image_exists:
                command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version} -mode dynamic -local {local_path} -nopull"
            else:
                command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version} -mode dynamic -local {local_path}"
        else:
            if package_version == "latest":
                if image_exists:
                    command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -mode dynamic -nopull"
                else:
                    command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -mode dynamic"
            else:
                if image_exists:
                    command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version} -mode dynamic -nopull"
                else:
                    command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version} -mode dynamic"

        print(command)

        try:
            start_time = time.time()
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
            end_time = time.time()
            elapsed_time = (end_time - start_time) 
            
            logger.info(result.stdout)

            json_file_path = os.path.join("/tmp/results/", package_name.lower() + ".json")
            

            read_command = f"cat {json_file_path}"

            json_result = subprocess.run(read_command, shell=True,
                                         check=True, capture_output=True,
                                         text=True, encoding='utf-8')
            json_data = json.loads(json_result.stdout)
            reports = Report.generate_report(json_data)
            
            reports['packages'] = {
                'package_name': package_name,
                'package_version': package_version,
                'ecosystem': ecosystem,
            }
            reports['time'] = elapsed_time

            # example of the reports to test the frontend
            # reports = {
            #     'packages': {            
            #         'package_name': package_name,
            #         'package_version': package_version,
            #         'ecosystem': ecosystem,
            #     },
            #     'time': 0.0,
            #     'install': {
            #         'num_files': 0,
            #         'num_commands': 0,
            #         'num_network_connections': 0,
            #         'num_system_calls': 0,
            #         'files': {
            #             'read': ['file1.txt', 'file2.txt'],
            #             'write': ['file3.txt'],
            #             'delete': ['file4.txt']
            #         },
            #         'dns': ['example.com', 'test.com'],
            #         'ips': [{'Address': '192.168.1.1', 'Port': 80}],
            #         'commands': ['ls', 'mkdir'],
            #         'syscalls': ['open', 'close']  
            #     },
            #     'execute': {
            #         'num_files': 0,
            #         'num_commands': 0,
            #         'num_network_connections': 0,
            #         'num_system_calls': 0,
            #         'files': {
            #             'read': ['file2.txt', 'file5.txt'],
            #             'write': ['file3.txt', 'file6.txt'],
            #             'delete': ['file4.txt']
            #         },
            #         'dns': ['example.com', 'new.com'],
            #         'ips': [{'Address': '192.168.1.1', 'Port': 80}, {'Address': '10.0.0.1', 'Port': 22}],
            #         'commands': ['mkdir', 'rm'],
            #         'syscalls': ['open', 'close', 'openat', 'openat', ....]
            #     }
            # }
    
            return reports
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the analysis: {e.stderr}")
            raise





class Report:

    @staticmethod
    def generate_report(json_data):
        results = {
            'install': {
                'num_files': 0,
                'num_commands': 0,
                'num_network_connections': 0,
                'num_system_calls': 0,
                'files': {
                    'read': [],
                    'write': [],
                    'delete': [],
                },
                'dns': [],
                'ips': [],
                'commands': [],
                'syscalls': []
            },
            'execute': {
                'num_files': 0,
                'num_commands': 0,
                'num_network_connections': 0,
                'num_system_calls': 0,
                'files': {
                    'read': [],
                    'write': [],
                    'delete': [],
                },
                'dns': [],
                'ips': [],
                'commands': [],
                'syscalls': []
            }
        }
        # generate a report based on the data
        # for now, just print the data to the console
        install_phase = json_data.get('Analysis', {}).get('install', {})

        results['install']['num_files'] = len(install_phase.get('Files') or [])
        results['install']['num_commands'] = len(install_phase.get('Commands') or [])
        results['install']['num_network_connections'] = len(install_phase.get('Sockets') or [])
        # for number of system calls divide by 2 because the system calls are 'enter' and 'exit' 
        # so we need to divide by 2 to get the actual number of system calls
        results['install']['num_system_calls'] = len(install_phase.get('Syscalls') or []) // 2

        for file in install_phase.get('Files', []):
            if file.get('Read'):
                results['install']['files']['read'].append(file.get('Path'))
            if file.get('Write'):
                results['install']['files']['write'].append(file.get('Path'))
            if file.get('Delete'):
                results['install']['files']['delete'].append(file.get('Path'))

        for dns in install_phase.get('DNS', []) or []:
            if dns is not None:
                for query in dns.get('Queries', []):
                    results['install']['dns'].append(query.get('Hostname'))
        
        for socket in install_phase.get('Sockets', []) or []:
            if socket is not None:
                results['install']['ips'].append({
                    'Address': socket.get('Address'), 
                    'Port': socket.get('Port'),
                    'Hostnames': ' '.join(socket.get('Hostnames') or [])
                })
        
        for command in install_phase.get('Commands', []) or []:
            if command is not None:
                results['install']['commands'].append(command.get('Command'))

        # pattern = re.compile(r'^Enter:\s*([\w]+)')
        pattern = re.compile(r'^Enter:\s*(.*)')
        for syscall in install_phase.get('Syscalls', []):
            if syscall is not None:
                match = pattern.match(syscall)
                if match:
                    results['install']['syscalls'].append(match.group(1))

        execution_phase = json_data.get('Analysis', {}).get('execute', {})
        if not execution_phase:
            execution_phase = json_data.get('Analysis', {}).get('import', {})

        results['execute']['num_files'] = len(execution_phase.get('Files') or [])
        results['execute']['num_commands'] = len(execution_phase.get('Commands') or [])
        results['execute']['num_network_connections'] = len(execution_phase.get('Sockets') or [])
        results['execute']['num_system_calls'] = len(execution_phase.get('Syscalls') or []) // 2

        for file in execution_phase.get('Files', []):
            if file.get('Read'):
                results['execute']['files']['read'].append(file.get('Path'))
            if file.get('Write'):
                results['execute']['files']['write'].append(file.get('Path'))

        for dns in execution_phase.get('DNS') or []:
            if dns is not None:
                for query in dns.get('Queries', []):
                    results['execute']['dns'].append(query.get('Hostname'))

        for socket in execution_phase.get('Sockets', []) or []:
            if socket is not None:
                results['execute']['ips'].append({
                    'Address': socket.get('Address'), 
                    'Port': socket.get('Port'),
                    'Hostnames': ' '.join(socket.get('Hostnames') or [])
                })
        
        for command in execution_phase.get('Commands', []) or []:
            if command is not None:
                results['execute']['commands'].append(command.get('Command'))
        


        # pattern = re.compile(r'^Enter:\s*([\w]+)')
        pattern = re.compile(r'^Enter:\s*(.*)')
        for syscall in execution_phase.get('Syscalls', []):
            if syscall is not None:
                match = pattern.match(syscall)
                if match:
                    results['execute']['syscalls'].append(match.group(1))
        
        return results
