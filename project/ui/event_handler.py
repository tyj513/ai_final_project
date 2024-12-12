
# ui/event_handler.py
import logging
from typing import List, Tuple, Dict
from ..core.data_models import UserPreference
from ..services import EnhancedFoodDetector

class UIEventHandler:
    """UI事件處理器"""
    def __init__(self, detector: EnhancedFoodDetector):
        self.detector = detector
        self.logger = logging.getLogger(__name__)

    def handle_profile_update(self, 
                            user_id: str,
                            dietary_restrictions: List[str],
                            cooking_skill: int,
                            preferred_cuisine: List[str],
                            health_goals: List[str],
                            equipment: List[str]) -> str:
        """處理用戶配置更新"""
        try:
            user_prefs = UserPreference(
                dietary_restrictions=dietary_restrictions,
                cooking_skill=cooking_skill,
                preferred_cuisine=preferred_cuisine,
                available_equipment=equipment,
                health_goals=health_goals,
                portion_size=2,
                max_cooking_time=60
            )
            
            if self.detector.user_manager.update_profile(user_id, user_prefs):
                return "設定已成功更新"
            return "設定更新失敗"
        except Exception as e:
            self.logger.error(f"Profile update error: {e}")
            return f"更新失敗: {str(e)}"

    def handle_image_processing(self, 
                              image_input,
                              user_id: str) -> Tuple[str, str]:
        """處理圖片輸入"""
        try:
            ingredients, recipe = self.detector.detect_ingredients(image_input)
            return ingredients, recipe
        except Exception as e:
            self.logger.error(f"Image processing error: {e}")
            return "處理失敗", str(e)

    def handle_rating_submission(self, 
                               user_id: str,
                               rating: float) -> str:
        """處理評分提交"""
        try:
            if self.detector.handle_rating_submission(user_id, rating):
                return "評分已提交"
            return "評分提交失敗"
        except Exception as e:
            self.logger.error(f"Rating submission error: {e}")
            return f"提交失敗: {str(e)}"

    def handle_history_load(self, user_id: str) -> Tuple[List[List], Dict]:
        """處理歷史記錄載入"""
        try:
            return self.detector.handle_history_load(user_id)
        except Exception as e:
            self.logger.error(f"History load error: {e}")
            return [], {"error": str(e)}