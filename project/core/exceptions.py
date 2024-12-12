class SystemError(Exception):
    """系統基礎異常類"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ConfigurationError(SystemError):
    """配置相關錯誤"""
    pass

class ProcessingError(SystemError):
    """處理過程中的錯誤"""
    pass

class ResourceError(SystemError):
    """資源相關錯誤"""
    pass

class ValidationError(SystemError):
    """數據驗證錯誤"""
    pass
