import os
import re
from typing import Dict
from typing import Optional
import mimetypes

# Assuming ArchiveMap is a dictionary of valid archive extensions
ArchiveMap: Dict[str, bool] = {
	".apk":    True,
	".bz2":    True,
	".bzip2":  True,
	".deb":    True,
	".gem":    True,
	".gz":     True,
	".jar":    True,
	".rpm":    True,
	".tar":    True,
	".tar.gz": True,
	".tar.xz": True,
	".tgz":    True,
	".upx":    True,
	".whl":    True,
	".xz":     True,
	".zip":    True,
}


def get_ext(path: str) -> str:
    base = os.path.basename(path)

    # Handle files with version numbers in the name
    # e.g. file1.2.3.tar.gz -> .tar.gz
    base = re.sub(r'\d+\.\d+\.\d+$', '', base)

    ext = os.path.splitext(base)[1]

    if ext and '.' in base:
        parts = base.split('.')
        if len(parts) > 2:
            sub_ext = f'.{parts[-2]}{ext}'
            if sub_ext in ArchiveMap:
                return sub_ext

    return ext

def is_supported_archive(path: str) -> bool:
    # Check if the file extension is in ArchiveMap
    if get_ext(path) in ArchiveMap:
        return True
        
    return False