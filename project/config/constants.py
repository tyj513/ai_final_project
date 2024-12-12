class Constants:
    """系統常量定義"""
    # 評分範圍
    MIN_RATING = 1
    MAX_RATING = 5
    
    # 食材相似度閾值
    INGREDIENT_SIMILARITY_THRESHOLD = 0.5
    
    # 系統狀態
    STATUS_HEALTHY = 'healthy'
    STATUS_WARNING = 'warning'
    STATUS_ERROR = 'error'
    
    # 快取鍵前綴
    RECIPE_CACHE_PREFIX = 'recipe:'
    USER_CACHE_PREFIX = 'user:'
    IMAGE_CACHE_PREFIX = 'image:'
    
    # 支援的圖像格式
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']
    
    # 默認值
    DEFAULT_COOKING_TIME = 60
    DEFAULT_PORTION_SIZE = 2
    DEFAULT_COOKING_SKILL = 3
    
    # LLM相關常量
    DEFAULT_MAX_TOKENS = 4000
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 0.9
    DEFAULT_REPEAT_PENALTY = 1.2
    
    # 系統監控相關
    MONITORING_INTERVAL = 30  # 秒
    CPU_WARNING_THRESHOLD = 90  # 百分比
    MEMORY_WARNING_THRESHOLD = 90  # 百分比
    GPU_MEMORY_WARNING_THRESHOLD = 90  # 百分比
