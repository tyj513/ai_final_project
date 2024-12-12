 

# managers/cache_manager.py
import redis
import logging
from typing import Any, Optional
from ..config import Constants

class CacheManager:
    """Redis快取管理器"""
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.cache_ttl = 3600
        self.logger = logging.getLogger(__name__)
        
    def get_cached(self, key: str) -> Optional[Any]:
        """從快取獲取數據"""
        try:
            data = self.redis_client.get(key)
            return eval(data.decode()) if data else None
        except Exception as e:
            self.logger.error(f"Cache retrieval error: {e}")
            return None
            
    def set_cached(self, key: str, value: Any, ttl: int = None) -> bool:
        """設置快取數據"""
        try:
            ttl = ttl or self.cache_ttl
            return self.redis_client.setex(key, ttl, str(value))
        except Exception as e:
            self.logger.error(f"Cache setting error: {e}")
            return False
            
    def invalidate(self, key: str) -> bool:
        """使快取失效"""
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            self.logger.error(f"Cache invalidation error: {e}")
            return False
            
    def get_stats(self) -> dict:
        """獲取快取統計信息"""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info['used_memory_human'],
                'hit_rate': info.get('keyspace_hits', 0) / (
                    info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)
                ) * 100,
                'total_keys': sum(
                    db_info['keys'] for db_name, db_info in info.items()
                    if db_name.startswith('db')
                )
            }
        except Exception as e:
            self.logger.error(f"Cache stats error: {e}")
            return {}
 