import os
import yara

class YaraRuleManager:
    def __init__(self):
        self.rules = {}
        self.load_rules()
    
    def load_rules(self):
        # Load rules from yara rules directory
        rules_dir = os.path.join(os.path.dirname(__file__), 'rules')
        for rule_file in os.listdir(rules_dir):
            if rule_file.endswith('.yar'):
                rule_path = os.path.join(rules_dir, rule_file)
                self.rules[rule_file] = yara.compile(rule_path)
    
    def analyze_behavior(self, analysis_data):
        matches = []
        for rule_name, rule in self.rules.items():
            matches.extend(rule.match(data=analysis_data))
        return matches