from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """系統配置數據類""" 
    # 基礎路徑配置
    base_dir: Path = Path("/home/p76131694/FoodSAM-main/project/sam")
    foodsam_dir: Path = base_dir / "FoodSAM" 
    
    # 模型相關路徑
    model_dir: Path = base_dir / "models"  
    model_path: Path = model_dir / "Meta-Llama-3.1-8B-Instruct-Q6_K.gguf"

    image_dir: Path = Path("/home/p76131694/FoodSAM-main/FoodSAM/assets")
    output_dir: Path = Path("/home/p76131694/FoodSAM-main/FoodSAM/output") 
    log_dir: Path = Path("logs")
    cache_dir: Path = Path("cache")
    
    # 數據文件路徑
    ingredients_path: Path = Path("/home/p76131694/FoodSAM-main/RAW_interactions.csv")
    recipes_path: Path = Path("/home/p76131694/FoodSAM-main/RAW_recipes.csv")
    user_interactions_path: Path = Path("/home/p76131694/FoodSAM-main/user_interactions.csv")
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600
    
    # 系統參數
    max_workers: int = 4
    gpu_memory_limit: int = 1000
    batch_size: int = 128
    model_context_size: int = 512
    
    # UI配置
    server_port: int = 7864
    server_name: str = "0.0.0.0"
    ui_height: int = 800
    
    def __post_init__(self):
        """初始化後確保所有目錄存在"""
        for path in [self.image_dir, self.output_dir, self.log_dir, self.cache_dir]:
            path.mkdir(parents=True, exist_ok=True)