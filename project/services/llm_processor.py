# project/services/llm_processor.py
import torch
import logging
from typing import List, Dict, Optional
from llama_cpp import Llama
from ..config import Config
from ..core.data_models import UserPreference, RecipeGenerationConfig
from ..managers import GPUMemoryManager
import pandas as pd 
# project/services/llm_processor.py
import os
import tempfile
from pathlib import Path

def setup_gradio_temp():
    """設置 Gradio 臨時目錄"""
    # 在用戶目錄下創建臨時目錄
    temp_dir = Path.home() / 'gradio_temp'
    os.makedirs(temp_dir, exist_ok=True)
    
    # 設置權限為 755
    temp_dir.chmod(0o755)
    
    # 設置環境變數
    os.environ['GRADIO_TEMP_DIR'] = str(temp_dir)
    
    return temp_dir

# 修改主程序 
class LLMProcessor:
    """LLM處理和食譜生成系統"""
    def __init__(self, config: Config):
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        
        # Initialize other components
        self.config = config
        self.gpu_manager = GPUMemoryManager(config.gpu_memory_limit)
        
        try:
            self.llm = self._initialize_llm()
            self.recipe_templates = self._load_recipe_templates()
        except Exception as e:
            self.logger.error(f"LLM initialization failed: {e}")
            self.llm = None
            self.logger.warning("LLM service is temporarily disabled - model file not found")



    def _validate_config(self):
        """驗證配置"""
        try:
            # 檢查模型路徑
            self.logger.info(f"Checking model path: {self.config.model_path}")
            if not self.config.model_path.exists():
                raise FileNotFoundError(f"Model file not found at: {self.config.model_path}")

            # 檢查GPU可用性
            if torch.cuda.is_available():
                self.logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            else:
                self.logger.warning("No GPU available, using CPU mode")

            # 檢查其他必要的配置
            self.logger.info(f"Model context size: {self.config.model_context_size}")
            self.logger.info(f"Batch size: {self.config.batch_size}")
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            raise

    def _initialize_llm(self) -> Optional[Llama]:
        """初始化LLM模型"""
        try:
            self.logger.info("Starting LLM initialization...")
            
            # Validate configuration before initializing
            self._validate_config()
            
            llm_params = {
                "model_path": str(self.config.model_path),
                "n_ctx": self.config.model_context_size,
                "n_batch": self.config.batch_size,
                "n_threads": 2,
                "n_gpu_layers": 12,
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            }
            
            self.logger.info(f"Initializing LLM with parameters: {llm_params}")
            with self.gpu_manager:
                llm = Llama(**llm_params)             
                
            self.logger.info("LLM initialization successful")
            return llm
            
        except Exception as e:
            detailed_error = f"LLM initialization error: {str(e)}, type: {type(e)}"
            self.logger.error(detailed_error)
            return None
 
    def generate_recipe(self, ingredients: List[str], user_prefs: Optional[UserPreference], similar_recipes: pd.DataFrame) -> str:
        """生成食譜"""
        if not self.llm:
            return f"""
為您找到的食材：{', '.join(ingredients)}
由於 LLM 模型初始化失敗，暫時無法生成詳細食譜。
請稍後重試或聯繫系統管理員。
            """
            
        try:
            prompt = self._build_prompt(ingredients, user_prefs, similar_recipes)
            response = self.llm.create_completion(
                prompt=prompt,
                max_tokens=self.config.model_context_size,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"Recipe generation error: {e}")
            return f"""
為您找到的食材：{', '.join(ingredients)}
生成食譜時發生錯誤，請稍後重試。
錯誤信息：{str(e)}
            """
    def _build_prompt(self,
                     ingredients: List[str],
                     user_prefs: Optional[UserPreference],
                     similar_recipes: pd.DataFrame) -> str:
        """構建生成提示"""
        prompt_parts = [
            f"Based on these ingredients: {', '.join(ingredients)}",
            self._format_dietary_restrictions(user_prefs),
            self._format_health_goals(user_prefs),
            self._format_cooking_constraints(user_prefs),
            f"Reference recipes:\n{similar_recipes.to_string()}"
        ]
        
        base_prompt = "\n\n".join(filter(None, prompt_parts))
        
        generation_instructions = """
        Please generate exactly 5 different recipe suggestions. For each recipe, include:
        1. Recipe name (numbered 1-5)
        2. Required ingredients (mark missing ingredients with **)
        3. Detailed cooking steps
        4. Cooking time and difficulty level
        5. Complete nutrition facts
        6. Health benefits

        Make sure to provide all 5 recipes with complete information for each one.
        Number each recipe clearly (1-5).
        Please respond in Traditional Chinese.
        """
        
        return f"{base_prompt}\n\n{generation_instructions}"

    def _format_dietary_restrictions(self, user_prefs: Optional[UserPreference]) -> str:
        """格式化飲食限制"""
        if not user_prefs or not user_prefs.dietary_restrictions:
            return ""
        return "Consider these dietary restrictions:\n" + \
               "\n".join(f"- {r}" for r in user_prefs.dietary_restrictions)

    def _format_health_goals(self, user_prefs: Optional[UserPreference]) -> str:
        """格式化健康目標"""
        if not user_prefs or not user_prefs.health_goals:
            return ""
        return "Optimize for these health goals:\n" + \
               "\n".join(f"- {g}" for g in user_prefs.health_goals)

    def _format_cooking_constraints(self, user_prefs: Optional[UserPreference]) -> str:
        """格式化烹飪限制"""
        if not user_prefs:
            return ""
        return f"""Cooking constraints:
        - Skill Level: {user_prefs.cooking_skill}/5
        - Maximum Cooking Time: {user_prefs.max_cooking_time} minutes
        - Available Equipment: {', '.join(user_prefs.available_equipment)}
        - Portion Size: {user_prefs.portion_size} servings"""

