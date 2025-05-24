# from ..src.yara.yara_manager import YaraRuleManager
# /web/package-analysis-web/package_analysis/test/test_yara.py", line 1, in <module>
#     from ..src.yara.yara_manager import YaraRuleManager
# ImportError: attempted relative import with no known parent package



import json
import os
import re

from typing import List, Dict, Optional
from dataclasses import dataclass, field

file_path = "/tmp/results/requests.json"
from yara_manager import YaraRuleManager


with open(file_path, 'r') as f:
    data = json.load(f)

class Report:

    @staticmethod
    def generate_report(json_data):
        # Initialize lists for commands, domains, and system calls
        commands = []
        domains = []
        system_calls = []

        # Process install phase
        install_phase = json_data.get('Analysis', {}).get('install', {})
        
        # Process commands
        for command in install_phase.get('Commands', []) or []:
            if command is not None:
                cmd = command.get('Command')
                if cmd:
                    # If cmd is a list, join it with spaces
                    if isinstance(cmd, list):
                        cmd = ' '.join(cmd)
                    commands.append({
                        'command': cmd,
                        'rules': []  # Will be populated by Yara analysis
                    })

        # Process DNS entries
        for dns in install_phase.get('DNS', []) or []:
            if dns is not None:
                for query in dns.get('Queries', []):
                    hostname = query.get('Hostname')
                    if hostname:
                        domains.append({
                            'domain': hostname,
                            'rules': []  # Will be populated by Yara analysis
                        })

        # Process system calls
        pattern = re.compile(r'^Enter:\s*(.*)')
        for syscall in install_phase.get('Syscalls', []):
            if syscall is not None:
                match = pattern.match(syscall)
                if match:
                    syscall_name = match.group(1)
                    system_calls.append({
                        'system_call': syscall_name,
                        'rules': []  # Will be populated by Yara analysis
                    })

        # Process execution phase
        execution_phase = json_data.get('Analysis', {}).get('execute', {})
        if not execution_phase:
            execution_phase = json_data.get('Analysis', {}).get('import', {})

        # Process commands from execution phase
        for command in execution_phase.get('Commands', []) or []:
            if command is not None:
                cmd = command.get('Command')
                if cmd:
                    # If cmd is a list, join it with spaces
                    if isinstance(cmd, list):
                        cmd = ' '.join(cmd)
                    commands.append({
                        'command': cmd,
                        'rules': []  # Will be populated by Yara analysis
                    })

        # Process DNS entries from execution phase
        for dns in execution_phase.get('DNS') or []:
            if dns is not None:
                for query in dns.get('Queries', []):
                    hostname = query.get('Hostname')
                    if hostname:
                        domains.append({
                            'domain': hostname,
                            'rules': []  # Will be populated by Yara analysis
                        })

        # Process system calls from execution phase
        for syscall in execution_phase.get('Syscalls', []):
            if syscall is not None:
                match = pattern.match(syscall)
                if match:
                    syscall_name = match.group(1)
                    system_calls.append({
                        'system_call': syscall_name,
                        'rules': []  # Will be populated by Yara analysis
                    })

        # Add Yara analysis
        try:
            yara_manager = YaraRuleManager()
            
            # Analyze commands
            command_text = '\n'.join([cmd['command'] for cmd in commands])
            command_matches = yara_manager.analyze_behavior(command_text)
            
            # Analyze domains
            domain_text = '\n'.join([domain['domain'] for domain in domains])
            network_matches = yara_manager.analyze_behavior(domain_text)
            
            # Analyze system calls
            syscall_text = '\n'.join([syscall['system_call'] for syscall in system_calls])
            syscall_matches = yara_manager.analyze_behavior(syscall_text)
            
            # Add Yara results to commands
            for match in command_matches:
                rule = {
                    'name': match.rule,
                    'description': '',  # You might want to add description from your Yara rules
                    'severity': 'high',  # You might want to add severity from your Yara rules
                    'strings': [str(s) for s in match.strings]
                }
                for cmd in commands:
                    if any(str(s) in cmd['command'] for s in match.strings):
                        cmd['rules'].append(rule)

            # Add Yara results to domains
            for match in network_matches:
                rule = {
                    'name': match.rule,
                    'description': '',  # You might want to add description from your Yara rules
                    'severity': 'high',  # You might want to add severity from your Yara rules
                    'strings': [str(s) for s in match.strings]
                }
                for domain in domains:
                    if any(str(s) in domain['domain'] for s in match.strings):
                        domain['rules'].append(rule)

            # Add Yara results to system calls
            for match in syscall_matches:
                rule = {
                    'name': match.rule,
                    'description': '',  # You might want to add description from your Yara rules
                    'severity': 'high',  # You might want to add severity from your Yara rules
                    'strings': [str(s) for s in match.strings]
                }
                for syscall in system_calls:
                    if any(str(s) in syscall['system_call'] for s in match.strings):
                        syscall['rules'].append(rule)

        except Exception as e:
            print(f"Yara analysis error: {e}")

        # Return data in the format that matches the Report class
        return {
            'commands': commands,
            'domains': domains,
            'system_calls': system_calls
        }


print(Report.generate_report(data)['commands'])


# create a class report
# in each command, domain, system call, there is a list of matching rules
# each rule has a name, description, severity, and a list of strings that matched

@dataclass
class Rule:
    name: str
    description: str
    severity: str
    strings: List[str]

@dataclass
class Command:
    command: str
    rules: List[Rule]

@dataclass
class Domain:
    domain: str
    rules: List[Rule]

@dataclass
class SystemCall:
    system_call: str
    rules: List[Rule]


@dataclass
class Report:
    commands: List[Command]
    domains: List[Domain]
    system_calls: List[SystemCall]

    def __init__(self, data: Dict):
        self.commands = []
        self.domains = []
        self.system_calls = []

        for command in data['commands']:
            command_obj = Command(command['command'], [])
            for rule in command['rules']:
                rule_obj = Rule(rule['name'], rule['description'], rule['severity'], rule['strings'])
                command_obj.rules.append(rule_obj)
            self.commands.append(command_obj)

        for domain in data['domains']:
            domain_obj = Domain(domain['domain'], [])
            for rule in domain['rules']:
                rule_obj = Rule(rule['name'], rule['description'], rule['severity'], rule['strings'])
                domain_obj.rules.append(rule_obj)
            self.domains.append(domain_obj)

        for system_call in data['system_calls']:
            system_call_obj = SystemCall(system_call['system_call'], [])
            for rule in system_call['rules']:
                rule_obj = Rule(rule['name'], rule['description'], rule['severity'], rule['strings'])
                system_call_obj.rules.append(rule_obj)
            self.system_calls.append(system_call_obj)

        # calculate the overall severity
        self.overall_severity = self.calculate_overall_severity()

    def calculate_overall_severity(self):
        # calculate the overall severity
        # the overall severity is the highest severity of all the rules
        return max(rule.severity for command in self.commands for rule in command.rules)




