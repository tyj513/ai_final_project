 
# main.py
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

# project/main.py
from project.config import Config
from project.utils import setup_logging, SystemMonitor
from project.services import EnhancedFoodDetector
from project.ui import UIComponents
from project.managers import SystemManager

class FoodSystemApplication:
    """食譜系統應用程式"""
    def __init__(self):
        self.config = self._load_config()
        self.logger = setup_logging(
            self.config.log_dir / 'food_system.log'
        )
        self.system_manager = SystemManager(self.config)
        self.system_monitor = SystemMonitor()
        
    def _load_config(self) -> Config:
        """載入配置"""
        try:
            return Config()
        except Exception as e:
            print(f"Error loading config: {e}")
            raise

    async def start(self):
        """啟動應用程式"""
        try:
            # 初始化系統
            await self.system_manager.initialize()
            
            # 啟動系統監控
            self.system_monitor.start_monitoring()
            
            # 創建檢測器
            detector = EnhancedFoodDetector(self.config)
            
            # 創建UI
            ui = UIComponents(detector)
            demo = ui.create_main_interface()
            
            # 啟動UI
            await demo.launch(
                server_port=self.config.server_port,
                server_name=self.config.server_name,
                show_error=True,
                height=self.config.ui_height
            )
            
        except Exception as e:
            self.logger.error(f"Application start failed: {e}")
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """關閉應用程式"""
        try:
            # 停止監控
            self.system_monitor.stop_monitoring()
            
            # 關閉系統
            await self.system_manager.shutdown()
            
            self.logger.info("Application shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

async def main():
    """主程式入口"""
    app = None
    try:
        app = FoodSystemApplication()
        await app.start()
    except KeyboardInterrupt:
        logging.info("Application shutdown by user")
    except Exception as e:
        logging.error(f"Application crash: {str(e)}")
    finally:
        if app:
            await app.shutdown()

if __name__ == "__main__":
    # Windows環境相容性設置
    if os.name == 'nt':
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )
    
    # 運行主程式
    asyncio.run(main())