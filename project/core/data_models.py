from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class UserPreference:
    """用戶偏好數據類"""
    dietary_restrictions: List[str]
    cooking_skill: int
    preferred_cuisine: List[str]
    available_equipment: List[str]
    health_goals: List[str]
    portion_size: int
    max_cooking_time: int

@dataclass
class RecipeGenerationConfig:
    """食譜生成配置"""
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    repeat_penalty: float = 1.2
    nutrition_required: bool = True
    detailed_steps: bool = True
    include_tips: bool = True
    max_recipes: int = 5