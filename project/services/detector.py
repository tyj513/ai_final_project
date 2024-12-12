import time
from typing import List, Dict, Tuple

# services/detector.py
import os
import subprocess
import logging
import torch
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Optional
 
 
from project.config import Config
from project.core.exceptions import ProcessingError
from project.managers import CacheManager, GPUMemoryManager
from project.services.llm_processor import LLMProcessor
from project.services.recipe_searcher import RecipeSearcher

class EnhancedFoodDetector:
    """食材檢測服務"""
    def __init__(self, config: Config):
        self.config = config
        self.cache_manager = CacheManager()
        self.gpu_manager = GPUMemoryManager(config.gpu_memory_limit)
        self.llm_processor = LLMProcessor(config)
        self.recipe_searcher = RecipeSearcher(config)
        self.logger = logging.getLogger(__name__)

    def detect_ingredients(self, image_input) -> Tuple[str, str]:
        """從圖片中檢測食材並生成食譜"""
        try:
            if image_input is None:
                return "請上傳圖片", ""
                
            # 檢查快取
            image_hash = self._calculate_image_hash(image_input)
            cache_key = f"ingredients:{image_hash}"
            
            cached_result = self.cache_manager.get_cached(cache_key)
            if cached_result:
                return cached_result, self._generate_recipe(cached_result.split(','))

            # 執行 FoodSAM 檢測
            ingredients = self._run_detection(image_input)
            
            # 更新快取
            self.cache_manager.set_cached(cache_key, ingredients)

            # 生成食譜
            recipe = self._generate_recipe(ingredients.split(','))

            return ingredients, recipe

        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            return f"檢測失敗: {str(e)}", "" 
        
 

    def _run_detection(self, image_path: str) -> str:
        """運行 FoodSAM 檢測"""
        try:
            os.chdir(self.config.foodsam_dir)
            result = subprocess.run(
                ['python', 'FoodSAM/FoodSAM/panoptic.py',  # 修改為正確的相對路徑
                '--img_path', str(image_path), 
                '--output', str(self.config.output_dir)],
                capture_output=True,
                text=True,
                check=True
            )

            # 從輸出文件讀取檢測結果
            output_path = self.config.output_dir / Path(image_path).stem / "sam_mask_label/sam_mask_label.txt"
            
            if not output_path.exists():
                raise ProcessingError("檢測輸出文件未找到")

            df = pd.read_csv(output_path)
            valid_items = df[
                (df['category_id'] != 0) & 
                (df['category_count_ratio'] > 0.5)
            ]['category_name'].unique()
            
            return ', '.join(valid_items) if len(valid_items) else "未檢測到食材"

        except Exception as e:
            raise ProcessingError(f"Food detection failed: {str(e)}")

    def _generate_recipe(self, ingredients: List[str]) -> str:
        """根據檢測到的食材生成食譜"""
        try:
            return self.llm_processor.generate_recipe(
                ingredients=ingredients,
                user_prefs=None,
                similar_recipes=self.recipe_searcher.search_recipes(ingredients)
            )
        except Exception as e:
            self.logger.error(f"Recipe generation error: {e}")
            return "無法生成食譜"

    def _calculate_image_hash(self, image_input) -> str:
        """計算圖片哈希值"""
        import hashlib
        from PIL import Image
        import io

        try:
            if isinstance(image_input, str):
                with open(image_input, 'rb') as f:
                    content = f.read()
            elif isinstance(image_input, Image.Image):
                byte_arr = io.BytesIO()
                image_input.save(byte_arr, format='PNG')
                content = byte_arr.getvalue()
            elif isinstance(image_input, bytes):
                content = image_input
            else:
                raise ValueError(f"Unsupported image type: {type(image_input)}")
            
            return hashlib.md5(content).hexdigest()
        except Exception as e:
            self.logger.error(f"Image hash calculation error: {e}")
            return str(time.time())
    def handle_rating_submission(self, user_id: str, rating: float) -> str:
        """處理評分提交"""
        try:
            if not user_id:
                return "請輸入用戶ID"
            
            # 記錄評分
            success = self.cache_manager.set_cached(
                f"rating:{user_id}:current_recipe",
                {
                    'rating': float(rating),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            if success:
                self.logger.info(f"Rating submitted for user {user_id}: {rating}")
                return "評分已成功提交！"
            else:
                return "評分提交失敗，請稍後重試"
                
        except Exception as e:
            self.logger.error(f"Rating submission error: {e}")
            return f"評分提交出錯: {str(e)}"

    def handle_profile_update(self, 
                            user_id: str,
                            dietary_restrictions: List[str],
                            cooking_skill: int,
                            preferred_cuisine: List[str],
                            health_goals: List[str],
                            equipment: List[str]) -> str:
        """處理用戶配置更新"""
        try:
            if not user_id:
                return "請輸入用戶ID"
                
            # 創建用戶偏好對象
            preferences = {
                'dietary_restrictions': dietary_restrictions,
                'cooking_skill': cooking_skill,
                'preferred_cuisine': preferred_cuisine,
                'available_equipment': equipment,
                'health_goals': health_goals,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 更新用戶配置
            success = self.cache_manager.set_cached(f"profile:{user_id}", preferences)
            
            if success:
                self.logger.info(f"Profile updated for user {user_id}")
                return "用戶配置已成功更新！"
            else:
                return "配置更新失敗，請稍後重試"
                
        except Exception as e:
            self.logger.error(f"Profile update error: {e}")
            return f"配置更新出錯: {str(e)}"

    def handle_history_load(self, user_id: str) -> Tuple[List[List], Dict]:
        """處理歷史記錄載入"""
        try:
            if not user_id:
                return [[]], {"error": "請輸入用戶ID"}
            
            # 獲取用戶評分歷史
            history = self.cache_manager.get_cached(f"rating:{user_id}:*") or []
            
            # 格式化數據
            rows = [
                [
                    str(record.get('timestamp', '')),
                    'current_recipe',
                    float(record.get('rating', 0))
                ]
                for record in history
            ]
            
            if not rows:
                rows = [['' for _ in range(3)]]
            
            # 生成統計信息
            stats = {
                'total_ratings': len(history),
                'average_rating': sum(r.get('rating', 0) for r in history) / len(history) if history else 0,
                'last_rating': history[-1].get('timestamp') if history else None
            }
            
            return rows, stats
            
        except Exception as e:
            self.logger.error(f"History load error: {e}")
            return [[]], {"error": str(e)}