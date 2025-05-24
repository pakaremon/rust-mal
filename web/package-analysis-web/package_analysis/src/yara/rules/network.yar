rule SuspiciousNetworkActivity: high {
    meta:
        description = "Detect suspicious network connections and data exfiltration"
        severity = "HIGH"
    strings:
        $suspicious_domains = /(burpcollaborator\.net|pipedream\.com|interact\.sh|ngrok\.io)/
        $data_exfil = /(POST|GET)\s+.*\s+HTTP\/\d\.\d/
        $ip_pattern = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
    condition:
        any of them
}