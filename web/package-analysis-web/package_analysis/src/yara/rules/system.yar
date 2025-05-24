rule SuspiciousSystemCalls: high {
    meta:
        description = "Detect suspicious system calls"
        severity = "HIGH"
    strings:
        $file_ops = /(open|write|read|delete|remove|unlink)/
        $network_ops = /(connect|bind|listen|accept)/
        $process_ops = /(fork|exec|spawn|kill)/
    condition:
        any of them
}