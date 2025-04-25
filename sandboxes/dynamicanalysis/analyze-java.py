#!/usr/bin/env python3
import os
import sys
import subprocess
import traceback
import zipfile
from dataclasses import dataclass
from typing import Optional

@dataclass
class Package:
    name: str
    version: Optional[str] = None
    local_path: Optional[str] = None

    def get_dependency_xml(self):
        group_id, artifact_id = self.name.split(":")
        if self.local_path:
            return f'''<dependency>
  <groupId>{group_id}</groupId>
  <artifactId>{artifact_id}</artifactId>
  <version>{self.version or "LATEST"}</version>
  <scope>system</scope>
  <systemPath>{os.path.abspath(self.local_path)}</systemPath>
</dependency>'''
        elif self.version:
            return f'''<dependency>
  <groupId>{group_id}</groupId>
  <artifactId>{artifact_id}</artifactId>
  <version>{self.version}</version>
</dependency>'''
        else:
            return f'''<dependency>
  <groupId>{group_id}</groupId>
  <artifactId>{artifact_id}</artifactId>
  <version>LATEST</version>
</dependency>'''

def install(package: Package):
    try:
        with open("pom.xml", 'r+') as pom:
            content = pom.read()
            xml = package.get_dependency_xml()
            if "<dependencies>" in content:
                content = content.replace("<dependencies>", "<dependencies>\n" + xml)
            else:
                content += "\n<dependencies>\n" + xml + "\n</dependencies>\n"
            pom.seek(0)
            pom.write(content)
            pom.truncate()

        subprocess.check_output(['mvn', 'compile'], stderr=subprocess.STDOUT)
        print('Install succeeded')
    except subprocess.CalledProcessError as e:
        print(e.output.decode())
        raise

def get_jar_path(package: Package):
    artifact = f"{package.name}:{package.version}"
    subprocess.check_output([
        'mvn', 'dependency:copy',
        f'-Dartifact={artifact}',
        '-DoutputDirectory=target/dependency',
        '-Dmdep.useBaseVersion=true'
    ], stderr=subprocess.STDOUT)

    group_id, artifact_id = package.name.split(':')
    jar_name = f"{artifact_id}-{package.version}.jar"
    return os.path.join("target", "dependency", jar_name)

def extract_top_level_packages(jar_path):
    packages = set()
    with zipfile.ZipFile(jar_path, 'r') as jar:
        for name in jar.namelist():
            if name.endswith('.class') and '$' not in name:
                package = '.'.join(name.split('/')[:-1])
                if package:
                    packages.add(package)
    return sorted(packages)

def importPkg(package: Package):
    try:
        jar_path = package.local_path if package.local_path else get_jar_path(package) 
        packages = extract_top_level_packages(jar_path)
        packages = [pk for pk in packages if not pk.startswith('java.') and not pk.startswith('META-INF.')]

        main_java_path = os.path.join('src', 'main', 'java', 'Main.java')
        os.makedirs(os.path.dirname(main_java_path), exist_ok=True)

        with open(main_java_path, 'w') as f:
            f.write("// Auto-generated import test\n")
            for pkg in packages:
                f.write(f"import {pkg}.*;\n")

            f.write("\npublic class Main {\n")
            f.write("    public static void main(String[] args) {\n")
            f.write(f'        System.out.println("Testing {package.name}");\n')
            f.write("    }\n}\n")

        subprocess.check_output(['mvn', 'compile'], stderr=subprocess.STDOUT)
        subprocess.check_output(['mvn', 'exec:java', '-Dexec.mainClass=Main'], stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as e:
        print("Failed during import/compile:")
        print(e.output.decode())
        traceback.print_exc()

# TODO: handle error at import phase in local file analysis
PHASES = {
    "all": [install, importPkg],
    "install": [install],
    "import": [importPkg],
}

def main():
    args = list(sys.argv)
    script = args.pop(0)
    '''
        for local file, support file .jar 
    '''
    if len(args) < 2 or len(args) > 4:
        raise ValueError(f'Usage: {script} [--local file | --version version] phase package_name (groupId:artifactId)')

    local_path = None
    version = None
    if args[0] == '--local':
        args.pop(0)
        local_path = args.pop(0)
    elif args[0] == '--version':
        args.pop(0)
        version = args.pop(0)

    phase = args.pop(0)
    package_name = args.pop(0)

    if not phase in PHASES:
        print(f'Unknown phase: {phase}')
        exit(1)

    package = Package(name=package_name, version=version, local_path=local_path)

    for func in PHASES[phase]:
        func(package)

if __name__ == '__main__':
    main()
