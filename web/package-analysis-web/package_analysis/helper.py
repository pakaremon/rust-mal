import requests
import tempfile
import subprocess
import json
import os
import time
import re
import git
from collections import defaultdict
from functools import lru_cache

from bs4 import BeautifulSoup



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
            return {"packages": packages}
        
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
    def handle_uploaded_file(file_path):
        # /media/listing-0_UwODAKy.1-r0.apk

        local_path = Helper.find_root_path() + '/web/package-analysis-web' + file_path
        package_name = file_path.split("/")[-1].split("-")[0]
        package_version = file_path.split("/")[-1].split("-")[1].split(".crate")[0]
        return Helper.run_package_analysis(package_name, package_version, "crates.io", local_path=local_path)


    @staticmethod
    def run_oss_find_source(package_name, package_version, ecosystem):
        
        ecosystem = Helper.transfer_ecosystem(ecosystem)
        folder_path = os.path.join(tempfile.gettempdir(), "oss-find-source")
        dst = os.path.join(folder_path, f"{package_name}.sarif")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        if Helper.is_windows_environment():
            executable = r"D:\HocTap\projectDrVuDucLy\tools\OSSGadget-0.1.422\src\oss-find-source\bin\Debug\net8.0\oss-find-source.exe"
        else:
            executable = r"oss-find-source"

        command = f'{executable} -o "{dst}" --format sarifv2 pkg:{ecosystem}/{package_name}'

        print(f"find source for package: {package_name}, version: {package_version}, ecosystem: {ecosystem}")
        print(f"Command: {command}")
        print(f"Output saved to {dst}")

        def parse_sarif(sarif_file):
            try:
                with open(os.path.join(sarif_file), 'r') as f:
                    data = json.load(f)
                    url_sources = []
                    for candidate in data['runs'][0]['results']:
                        if candidate:
                            url_sources.append(candidate['locations'][0]['physicalLocation']['address']['fullyQualifiedName'])
                        
                    return url_sources
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return []
            except FileNotFoundError as e:
                print(f"File not found: {e}")
                return []
            
        try:
            if os.path.exists(dst):
                url_sources = parse_sarif(dst)
                return url_sources
            
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"Command executed successfully: {command}")

            url_sources = parse_sarif(dst)
            print(f"URL sources found: {url_sources}")
            
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
        else:
            raise ValueError(f"Unknown ecosystem: {ecosystem}")

    @staticmethod
    def run_oss_squats(package_name, package_version, ecosystem):

        print(f"find typosquats for package: {package_name}, version: {package_version}, ecosystem: {ecosystem}")
        ecosystem = Helper.transfer_ecosystem(ecosystem)
        folder_path = os.path.join(tempfile.gettempdir(), "oss-find-squats")
        dst = os.path.join(folder_path, f"{package_name}.sarif")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if Helper.is_windows_environment():
            executable = r"D:\HocTap\projectDrVuDucLy\tools\OSSGadget-0.1.422\src\oss-find-squats\bin\Debug\net8.0\oss-find-squats.exe" 
        else:
            executable = r"oss-find-squats"
        command = f'{executable} -o "{dst}" --format sarifv2 pkg:{ecosystem}/{package_name}'


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
            
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"Command executed successfully: {command}")

            print(f"Output saved to {dst}")
            package_names = parse_sarif(dst)
            print(f"Package names found: {package_names}")
            
            return package_names

        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")
            raise #always raise the error to the caller
        
        

 
    @staticmethod
    def run_package_analysis(package_name, package_version, ecosystem, local_path=None):
        print(f" Run package-analysis: Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
        # ./scripts/run_analysis.sh -ecosystem Rust -package littlest -version littlest.0.0.0  -local /path/fijiwashere12323-0.0.0-r0.apk -sandbox-image 'wolfi-apk/dynamic-analysis'   -analysis-command 'analyze_wolfi_apk.py' -mode dynamic -nopull 
        # run the script with the package name, version, ecosystem and the path to the apk
        # the script should return the results of the analysis
        # for now, just print the command to the console

        script_path = Helper.find_script_path()
        if local_path:
            command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version}  -mode dynamic -local {local_path}"
            print(command)
        else:
            command = f"{script_path} -ecosystem {ecosystem} -package {package_name} -version {package_version}  -mode dynamic" 

        if Helper.is_windows_environment():
            command = f"wsl {command}"

        try:
            start_time = time.time()
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            end_time = time.time()
            elapsed_time = (end_time - start_time) 
            print(result.stdout)

            json_file_path = os.path.join("/tmp/results/", package_name + ".json")
            
            if Helper.is_windows_environment():
                read_command = f"wsl cat {json_file_path}"
            else:
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
            #         'syscalls': ['open', 'close']
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
            'import': {
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

        results['import']['num_files'] = len(execution_phase.get('Files', []))
        results['import']['num_commands'] = len(execution_phase.get('Commands', []))
        results['import']['num_network_connections'] = len(execution_phase.get('Sockets', []))
        results['import']['num_system_calls'] = len(execution_phase.get('Syscalls', [])) // 2

        for file in execution_phase.get('Files', []):
            if file.get('Read'):
                results['import']['files']['read'].append(file.get('Path'))
            if file.get('Write'):
                results['import']['files']['write'].append(file.get('Path'))

        for dns in execution_phase.get('DNS') or []:
            if dns is not None:
                for query in dns.get('Queries', []):
                    results['import']['dns'].append(query.get('Hostname'))

        for socket in execution_phase.get('Sockets', []) or []:
            if socket is not None:
                results['import']['ips'].append({
                    'Address': socket.get('Address'), 
                    'Port': socket.get('Port'),
                    'Hostnames': ' '.join(socket.get('Hostnames') or [])
                })
        
        for command in execution_phase.get('Commands', []) or []:
            if command is not None:
                results['import']['commands'].append(command.get('Command'))
        


        # pattern = re.compile(r'^Enter:\s*([\w]+)')
        pattern = re.compile(r'^Enter:\s*(.*)')
        for syscall in execution_phase.get('Syscalls', []):
            if syscall is not None:
                match = pattern.match(syscall)
                if match:
                    results['import']['syscalls'].append(match.group(1))
        
        return results
