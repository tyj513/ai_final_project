import hashlib
import re
from pathlib import Path
from typing import Union, Any

def calculate_hash(content: Union[str, bytes]) -> str:
    """計算內容的雜湊值"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.md5(content).hexdigest()

def validate_path(path: Union[str, Path]) -> Path:
    """驗證並返回路徑對象"""
    path = Path(path)
    if not path.exists():
        raise ConfigurationError(f"Path does not exist: {path}")
    return path

def sanitize_input(text: str) -> str:
    """清理輸入文本"""
    # 移除特殊字符
    text = re.sub(r'[^\w\s-]', '', text)
    # 將多個空格替換為單個空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def validate_numeric(value: Any, min_value: float = None, max_value: float = None) -> float:
    """驗證數值"""
    try:
        value = float(value)
        if min_value is not None and value < min_value:
            raise ValidationError(f"Value {value} is less than minimum {min_value}")
        if max_value is not None and value > max_value:
            raise ValidationError(f"Value {value} is greater than maximum {max_value}")
        return value
    except ValueError:
        raise ValidationError(f"Invalid numeric value: {value}")