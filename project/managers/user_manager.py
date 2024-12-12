import json
import time
import logging
from typing import List, Dict, Optional
from collections import defaultdict
from ..core.data_models import UserPreference
from ..config import Constants
from .cache_manager import CacheManager

class UserProfileManager:
    """用戶配置管理系統"""
    def __init__(self, 
                 profile_path: str = "user_profiles.json",
                 interaction_path: str = "user_interactions.json",
                 cache_manager: Optional[CacheManager] = None):
        self.profile_path = profile_path
        self.interaction_path = interaction_path
        self.cache_manager = cache_manager or CacheManager()
        self.user_profiles = {}
        self.interaction_history = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
        self._ensure_files_exist()
        self._load_data()

    def _ensure_files_exist(self):
        """確保必要的檔案存在"""
        import os
        for file_path in [self.profile_path, self.interaction_path]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                self.logger.info(f"Created new file: {file_path}")

    def _load_data(self):
        """載入所有用戶數據"""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.user_profiles = json.load(f)
            
            with open(self.interaction_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.interaction_history = defaultdict(list, data)
                
            self.logger.info("Successfully loaded user data")
        except Exception as e:
            self.logger.error(f"Error loading user data: {e}")

    def _save_data(self):
        """保存所有用戶數據"""
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profiles, f, ensure_ascii=False, indent=2)
            
            with open(self.interaction_path, 'w', encoding='utf-8') as f:
                json.dump(dict(self.interaction_history), f, ensure_ascii=False, indent=2)
                
            self.logger.info("Successfully saved user data")
        except Exception as e:
            self.logger.error(f"Error saving user data: {e}")

    def update_profile(self, user_id: str, preferences: UserPreference) -> bool:
        """更新用戶偏好設定"""
        try:
            self.user_profiles[user_id] = {
                'dietary_restrictions': preferences.dietary_restrictions,
                'cooking_skill': preferences.cooking_skill,
                'preferred_cuisine': preferences.preferred_cuisine,
                'available_equipment': preferences.available_equipment,
                'health_goals': preferences.health_goals,
                'portion_size': preferences.portion_size,
                'max_cooking_time': preferences.max_cooking_time,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            cache_key = f"user_profile:{user_id}"
            self.cache_manager.set_cached(cache_key, self.user_profiles[user_id])
            
            self._save_data()
            return True
        except Exception as e:
            self.logger.error(f"Error updating profile for user {user_id}: {e}")
            return False

    def get_user_preferences(self, user_id: str) -> Optional[UserPreference]:
        """獲取用戶偏好設定"""
        try:
            cache_key = f"user_profile:{user_id}"
            cached_data = self.cache_manager.get_cached(cache_key)
            
            if cached_data:
                profile = cached_data
            elif user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                self.cache_manager.set_cached(cache_key, profile)
            else:
                return None
                
            return UserPreference(**profile)
        except Exception as e:
            self.logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            return None

    def record_interaction(self, 
                         user_id: str, 
                         recipe_id: str, 
                         rating: float,
                         feedback: str = "") -> bool:
        """記錄用戶互動"""
        try:
            interaction = {
                'recipe_id': str(recipe_id),
                'rating': float(rating),
                'feedback': feedback,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.interaction_history[user_id].append(interaction)
            
            cache_key = f"user_interactions:{user_id}"
            self.cache_manager.set_cached(cache_key, self.interaction_history[user_id])
            
            self._save_data()
            return True
        except Exception as e:
            self.logger.error(f"Error recording interaction for user {user_id}: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict:
        """獲取用戶統計信息"""
        try:
            ratings = self.get_user_ratings(user_id)
            if not ratings:
                return {}
                
            return {
                'total_ratings': len(ratings),
                'average_rating': sum(r['rating'] for r in ratings) / len(ratings),
                'last_interaction': ratings[-1]['timestamp'] if ratings else None,
                'favorite_recipes': self._get_favorite_recipes(user_id, top_k=5)
            }
        except Exception as e:
            self.logger.error(f"Error calculating stats for user {user_id}: {e}")
            return {}

    def _get_favorite_recipes(self, user_id: str, top_k: int = 5) -> List[str]:
        """獲取用戶最喜歡的食譜"""
        try:
            ratings = self.get_user_ratings(user_id)
            sorted_recipes = sorted(ratings, key=lambda x: x['rating'], reverse=True)
            return [r['recipe_id'] for r in sorted_recipes[:top_k]]
        except Exception as e:
            self.logger.error(f"Error getting favorite recipes for user {user_id}: {e}")
            return []