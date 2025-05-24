rule SuspiciousCommandExecution: high {
    meta:
        description = "Detect suspicious command execution patterns"
        severity = "HIGH"
    strings:
        $shell_commands = /(bash|sh|cmd|powershell|wget|curl|nc|netcat|python|perl|ruby|php)\s+/
        $reverse_shell = /(nc|netcat)\s+.*\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9.-]+)\s+\d+/
        $system_calls = /(system|exec|eval|spawn|fork|popen)/
    condition:
        any of them
}