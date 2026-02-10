"""
文件哈希计算工具
支持 SHA256、MD5 等多种哈希算法
"""
import hashlib
from pathlib import Path
from typing import BinaryIO, Literal

HashAlgorithm = Literal["sha256", "md5", "sha1"]


def calculate_file_hash(
    file_path: str | Path,
    algorithm: HashAlgorithm = "sha256",
    chunk_size: int = 8192
) -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法（sha256/md5/sha1）
        chunk_size: 分块读取大小（字节）
        
    Returns:
        str: 十六进制哈希值
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的哈希算法
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 创建哈希对象
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    # 分块读取文件并计算哈希
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def calculate_stream_hash(
    stream: BinaryIO,
    algorithm: HashAlgorithm = "sha256",
    chunk_size: int = 8192
) -> str:
    """
    计算数据流哈希值
    
    Args:
        stream: 二进制数据流
        algorithm: 哈希算法（sha256/md5/sha1）
        chunk_size: 分块读取大小（字节）
        
    Returns:
        str: 十六进制哈希值
        
    Raises:
        ValueError: 不支持的哈希算法
    """
    # 创建哈希对象
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    # 分块读取流并计算哈希
    while chunk := stream.read(chunk_size):
        hasher.update(chunk)
    
    return hasher.hexdigest()


def calculate_bytes_hash(
    data: bytes,
    algorithm: HashAlgorithm = "sha256"
) -> str:
    """
    计算字节数据哈希值
    
    Args:
        data: 字节数据
        algorithm: 哈希算法（sha256/md5/sha1）
        
    Returns:
        str: 十六进制哈希值
        
    Raises:
        ValueError: 不支持的哈希算法
    """
    # 创建哈希对象
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    hasher.update(data)
    return hasher.hexdigest()


def verify_file_hash(
    file_path: str | Path,
    expected_hash: str,
    algorithm: HashAlgorithm = "sha256"
) -> bool:
    """
    验证文件哈希值
    
    Args:
        file_path: 文件路径
        expected_hash: 期望的哈希值
        algorithm: 哈希算法（sha256/md5/sha1）
        
    Returns:
        bool: 哈希值是否匹配
    """
    try:
        actual_hash = calculate_file_hash(file_path, algorithm)
        return actual_hash.lower() == expected_hash.lower()
    except Exception:
        return False


def calculate_multi_hash(
    file_path: str | Path,
    algorithms: list[HashAlgorithm] = None
) -> dict[str, str]:
    """
    计算文件的多种哈希值
    
    Args:
        file_path: 文件路径
        algorithms: 哈希算法列表，默认为 ["sha256", "md5"]
        
    Returns:
        dict: 算法名到哈希值的映射
        
    Example:
        >>> calculate_multi_hash("file.txt")
        {"sha256": "abc123...", "md5": "def456..."}
    """
    if algorithms is None:
        algorithms = ["sha256", "md5"]
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 创建所有哈希对象
    hashers = {}
    for algo in algorithms:
        if algo == "sha256":
            hashers[algo] = hashlib.sha256()
        elif algo == "md5":
            hashers[algo] = hashlib.md5()
        elif algo == "sha1":
            hashers[algo] = hashlib.sha1()
        else:
            raise ValueError(f"不支持的哈希算法: {algo}")
    
    # 一次性读取文件，同时计算所有哈希
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            for hasher in hashers.values():
                hasher.update(chunk)
    
    # 返回所有哈希值
    return {algo: hasher.hexdigest() for algo, hasher in hashers.items()}
