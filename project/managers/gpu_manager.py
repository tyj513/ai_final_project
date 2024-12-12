import gc
import torch
import logging
import threading
import time
from typing import Optional, Dict

class GPUMemoryManager:
    """GPU記憶體管理器"""
    def __init__(self, memory_limit_mb: int = 1000):
        self.memory_limit = memory_limit_mb * 1024 * 1024  # 轉換為位元組
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)

    def get_gpu_memory_info(self) -> Optional[Dict[str, int]]:
        """獲取GPU記憶體使用信息"""
        if torch.cuda.is_available():
            return {
                'allocated': torch.cuda.memory_allocated(0),
                'reserved': torch.cuda.memory_reserved(0)
            }
        return None

    def force_memory_release(self):
        """強制釋放GPU記憶體"""
        if not torch.cuda.is_available():
            return

        torch.cuda.empty_cache()
        gc.collect()
        
        if torch.cuda.memory_allocated(0) > self.memory_limit:
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.reset_max_memory_allocated()
            gc.collect()

    def start_monitoring(self):
        """開始監控GPU記憶體使用"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_memory)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止GPU記憶體監控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_memory(self):
        """記憶體監控線程"""
        while self.monitoring:
            memory_info = self.get_gpu_memory_info()
            if memory_info and memory_info['allocated'] > self.memory_limit:
                self.logger.warning(
                    f"GPU memory usage ({memory_info['allocated'] / 1024 / 1024:.2f}MB) "
                    f"exceeds limit ({self.memory_limit / 1024 / 1024:.2f}MB)"
                )
                self.force_memory_release()
            time.sleep(1)