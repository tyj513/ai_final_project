# services/recipe_searcher.py
import pandas as pd
import numpy as np
import logging
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from ..config import Config
from ..core.exceptions import ProcessingError
from ..managers import CacheManager

class RecipeSearcher:
    """食譜搜索和推薦引擎"""
    def __init__(self, config: Config):
        # 初始化組件
        self.config = config
        self.recipes = pd.read_csv(config.recipes_path)
        self.ingredients = pd.read_csv(config.ingredients_path) 
        self.cache_manager = CacheManager()
        self.recipe_searcher = RecipeSearcher(config)

        # 數據預處理 
        self._preprocess_data()
        self._calculate_recipe_embeddings()
        
        # 協同過濾組件
        self.collaborative_filter = CollaborativeFilter()

    def _preprocess_data(self):
        """數據預處理"""
        try:
            # 處理食材列表
            self.recipes['ingredients'] = self.recipes['ingredients'].apply(eval)
            self.recipes['steps'] = self.recipes['steps'].apply(eval)
            
            # 處理營養信息
            self.recipes['nutrition'] = self.recipes['nutrition'].apply(self._parse_nutrition)
            
            # 計算特徵向量
            self.recipe_features = self._calculate_recipe_features()
            
            self.logger.info("Recipe data preprocessing completed")
        except Exception as e:
            self.logger.error(f"Data preprocessing error: {e}")
            raise ProcessingError("Failed to preprocess recipe data")

    def _parse_nutrition(self, nutrition_str: str) -> Dict:
        """解析營養信息"""
        try:
            nutrition_list = eval(nutrition_str)
            return {
                'calories': nutrition_list[0],
                'total_fat': nutrition_list[1],
                'sugar': nutrition_list[2],
                'sodium': nutrition_list[3],
                'protein': nutrition_list[4],
                'saturated_fat': nutrition_list[5],
                'carbohydrates': nutrition_list[6]
            }
        except:
            return {
                'calories': 0, 'total_fat': 0, 'sugar': 0,
                'sodium': 0, 'protein': 0, 'saturated_fat': 0,
                'carbohydrates': 0
            }

    def _calculate_recipe_features(self) -> np.ndarray:
        """計算食譜特徵向量"""
        features = []
        for _, recipe in self.recipes.iterrows():
            recipe_features = [
                len(recipe['ingredients']),
                recipe['minutes'],
                self._calculate_difficulty(recipe),
                *self._extract_nutrition_features(recipe['nutrition'])
            ]
            features.append(recipe_features)
        return np.array(features)

    def _calculate_difficulty(self, recipe) -> float:
        """計算食譜難度"""
        steps_count = len(recipe['steps'])
        time_factor = min(recipe['minutes'] / 60, 2)
        equipment_factor = len(self._extract_equipment(recipe['steps']))
        return (steps_count * 0.4 + time_factor * 0.3 + equipment_factor * 0.3) / 3

    def _extract_nutrition_features(self, nutrition: Dict) -> List[float]:
        """提取營養特徵"""
        return [
            nutrition['calories'] / 1000,
            nutrition['protein'] / 100,
            nutrition['total_fat'] / 100,
            nutrition['carbohydrates'] / 100
        ]

    def _extract_equipment(self, steps: List[str]) -> List[str]:
        """提取所需設備"""
        equipment_keywords = ['oven', 'microwave', 'blender', 
                            'mixer', 'grill', 'pan', 'pot']
        required = set()
        for step in steps:
            for eq in equipment_keywords:
                if eq in step.lower():
                    required.add(eq)
        return list(required)

    def search_recipes(self, 
                      ingredients: List[str], 
                      user_id: str = None,
                      top_k: int = 5) -> pd.DataFrame:
        """搜索食譜"""
        try:
            # 檢查快取
            cache_key = f"recipe_search:{','.join(sorted(ingredients))}"
            cached_results = self.cache_manager.get_cached(cache_key)
            if cached_results is not None:
                return pd.DataFrame(cached_results)

            # 計算食材相似度
            ingredients = [ing.strip().lower() for ing in ingredients]
            ingredient_scores = self._calculate_ingredient_scores(ingredients)
            
            # 計算最終分數
            final_scores = ingredient_scores
            
            # 選擇最佳結果
            top_indices = np.argsort(final_scores)[-top_k:]
            results = self.recipes.iloc[top_indices][
                ['name', 'ingredients', 'steps', 'minutes', 'nutrition']
            ].to_dict('records')
            
            # 更新快取
            self.cache_manager.set_cached(cache_key, results)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            self.logger.error(f"Recipe search error: {e}")
            return pd.DataFrame()

    def _calculate_ingredient_scores(self, input_ingredients: List[str]) -> np.ndarray:
        """計算食材相似度分數"""
        scores = []
        for recipe_ingredients in self.recipes['ingredients']:
            recipe_ings = [ing.lower() for ing in recipe_ingredients]
            matches = sum(1 for ing in input_ingredients 
                         if any(ing in r for r in recipe_ings))
            scores.append(matches / len(input_ingredients))
        return np.array(scores)
# services/recipe_searcher.py

class CollaborativeFilter:
    """協同過濾推薦引擎"""
    def __init__(self, n_factors: int = 50):
        self.n_factors = n_factors
        self.user_matrix = None
        self.item_matrix = None
        self.user_bias = None
        self.item_bias = None
        self.global_mean = None
        self.user_mapping = {}  # 初始化映射字典
        self.item_mapping = {}
        self.logger = logging.getLogger(__name__)

    def get_recommendations(self, user_id: str = None) -> np.ndarray:
        """獲取推薦分數"""
        try:
            # 如果還沒有訓練數據，返回空陣列
            if not self.user_mapping or user_id not in self.user_mapping:
                self.logger.warning(f"No training data available for user {user_id}")
                # 返回一個與 item_matrix 形狀匹配的零陣列
                return np.zeros(100)  # 或其他合適的默認大小
                
            user_idx = self.user_mapping[user_id]
            user_vector = self.user_matrix[user_idx]
            
            # 計算預測評分
            predictions = self.global_mean + np.dot(user_vector, self.item_matrix.T)
            
            # 標準化分數到[0,1]範圍
            predictions = (predictions - predictions.min()) / (
                predictions.max() - predictions.min() + 1e-8)  # 避免除以零
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return np.zeros(100)  # 或其他合適的默認大小

# 修改 RecipeSearcher 類中的相關代碼
class RecipeSearcher:
    def search_recipes(self, 
                      ingredients: List[str], 
                      user_id: str = None,
                      top_k: int = 5) -> pd.DataFrame:
        """搜索食譜"""
        try:
            # 檢查快取
            cache_key = f"recipe_search:{','.join(sorted(ingredients))}"
            cached_results = self.cache_manager.get_cached(cache_key)
            if cached_results is not None:
                return pd.DataFrame(cached_results)

            # 計算食材相似度
            ingredients = [ing.strip().lower() for ing in ingredients]
            ingredient_scores = self._calculate_ingredient_scores(ingredients)
            
            # 如果有用戶ID，嘗試獲取協同過濾推薦分數
            cf_scores = np.zeros_like(ingredient_scores)  # 默認為零
            if user_id:
                try:
                    cf_scores = self.collaborative_filter.get_recommendations(user_id)
                    # 確保長度匹配
                    cf_scores = cf_scores[:len(ingredient_scores)]
                except Exception as e:
                    self.logger.warning(f"Failed to get collaborative filtering scores: {e}")
            
            # 計算最終分數 (只使用食材相似度)
            final_scores = ingredient_scores
            
            # 選擇最佳結果
            top_indices = np.argsort(final_scores)[-top_k:][::-1]  # 反轉順序，最高分在前
            results = self.recipes.iloc[top_indices][
                ['name', 'ingredients', 'steps', 'minutes', 'nutrition']
            ].to_dict('records')
            
            # 更新快取
            self.cache_manager.set_cached(cache_key, results)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            self.logger.error(f"Recipe search error: {e}")
            return pd.DataFrame()