import logging
import asyncio
import torch
from typing import Optional
from ..config import Config
from ..core.exceptions import SystemError
from .gpu_manager import GPUMemoryManager

class SystemManager:
    """系統管理器"""
    def __init__(self, config: Config):
        self.config = config
        self.gpu_manager = GPUMemoryManager(config.gpu_memory_limit)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_dir / 'food_system.log'),
                logging.StreamHandler()
            ]
        )

    async def initialize(self):
        """初始化系統"""
        try:
            self._setup_environment()
            await self._setup_gpu()
            self._create_directories()
            self.logger.info("System initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            raise SystemError(f"Initialization failed: {str(e)}")

    def _setup_environment(self):
        """設置環境變數"""
        import os
        os.environ['PYTHONPATH'] = f"{self.config.foodsam_dir}:{os.environ.get('PYTHONPATH', '')}"
        self.logger.info("Environment setup completed")

    async def _setup_gpu(self):
        """設置GPU環境"""
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            self.logger.info(f"Using GPU: {device_name}")
            self.gpu_manager.start_monitoring()
        else:
            self.logger.warning("No GPU available, using CPU")

    def _create_directories(self):
        """創建必要的目錄"""
        for path in [self.config.log_dir, self.config.cache_dir, 
                    self.config.output_dir, self.config.image_dir]:
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {path}")

    async def shutdown(self):
        """關閉系統"""
        try:
            self.gpu_manager.stop_monitoring()
            torch.cuda.empty_cache()
            self.logger.info("System shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise SystemError(f"Shutdown failed: {str(e)}")
