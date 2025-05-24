# Converted from Go to Python

import io
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Placeholder for yara-x rules (no direct Python equivalent from VT as of this writing)
class YaraRules:
    pass

# Renderer interface
class Renderer:
    def scanning(self, ctx, path: str):
        raise NotImplementedError

    def file(self, ctx, file_report):
        raise NotImplementedError

    def full(self, ctx, config, report):
        raise NotImplementedError

    def name(self) -> str:
        raise NotImplementedError

@dataclass
class Config:
    concurrency: int = 1
    exit_first_hit: bool = False
    exit_first_miss: bool = False
    file_risk_change: bool = False
    file_risk_increase: bool = False
    ignore_self: bool = False
    ignore_tags: List[str] = field(default_factory=list)
    include_data_files: bool = False
    min_file_risk: int = 0
    min_risk: int = 0
    oci: bool = False
    output: Optional[io.TextIOBase] = None
    processes: bool = False
    quantity_increases_risk: bool = False
    renderer: Optional[Renderer] = None
    rule_fs: List[str] = field(default_factory=list)  # Simulate fs.FS as list of paths
    rules: Optional[YaraRules] = None
    scan: bool = False
    scan_paths: List[str] = field(default_factory=list)
    stats: bool = False
    trim_prefixes: List[str] = field(default_factory=list)

@dataclass
class Behavior:
    description: Optional[str] = None
    match_strings: List[str] = field(default_factory=list)
    risk_score: int = 0
    risk_level: Optional[str] = None
    rule_url: Optional[str] = None
    reference_url: Optional[str] = None
    rule_author: Optional[str] = None
    rule_author_url: Optional[str] = None
    rule_license: Optional[str] = None
    rule_license_url: Optional[str] = None
    diff_added: bool = False
    diff_removed: bool = False
    id: Optional[str] = None
    rule_name: Optional[str] = None
    override: List[str] = field(default_factory=list)

@dataclass
class FileReport:
    path: str
    sha256: str
    size: int
    skipped: Optional[str] = None
    meta: Dict[str, str] = field(default_factory=dict)
    syscalls: List[str] = field(default_factory=list)
    pledge: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    behaviors: List[Behavior] = field(default_factory=list)
    filtered_behaviors: int = 0
    previous_path: Optional[str] = None
    previous_rel_path: Optional[str] = None
    previous_rel_path_score: float = 0.0
    previous_risk_score: int = 0
    previous_risk_level: Optional[str] = None
    risk_score: int = 0
    risk_level: Optional[str] = None
    is_malcontent: bool = False
    overrides: List[Behavior] = field(default_factory=list)
    archive_root: Optional[str] = None
    full_path: Optional[str] = None

@dataclass
class DiffReport:
    added: Dict[str, FileReport] = field(default_factory=dict)
    removed: Dict[str, FileReport] = field(default_factory=dict)
    modified: Dict[str, FileReport] = field(default_factory=dict)

@dataclass
class Report:
    files: Dict[str, FileReport] = field(default_factory=dict)
    diff: Optional[DiffReport] = None
    filter: Optional[str] = None

@dataclass
class IntMetric:
    count: int
    key: int
    total: int
    value: float

@dataclass
class StrMetric:
    count: int
    key: str
    total: int
    value: float

@dataclass
class CombinedReport:
    added: str
    added_fr: Optional[FileReport]
    removed: str
    removed_fr: Optional[FileReport]
    score: float
