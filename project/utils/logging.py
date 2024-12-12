 
import logging
from pathlib import Path
from typing import Union
import sys

def setup_logging(
    log_file: Union[str, Path],
    level: int = logging.INFO,
    format_str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> logging.Logger:
    """設置日誌系統"""
    # 創建日誌目錄
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置根日誌記錄器
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 檔案處理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(file_handler)
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(console_handler)
    
    return logger
 