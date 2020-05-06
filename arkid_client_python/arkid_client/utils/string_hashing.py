"""
Hash For Some Confidential Information
"""
import hashlib


def sha256_string(string):
    """将字符串进行 sha256 编码"""
    return hashlib.sha256(string.encode("utf-8")).hexdigest()
