# Intro to AI_final_project_75
# Food Ingredient Detection and Recipe Generation System Using Segment-Anything Model with Zero-Shot Learning 食材好，食才好

一個基於 AI 的智慧食譜推薦系統，能夠識別食材圖片並生成相應的食譜建議。

## 系統特點

- 🔍 食材圖像識別：使用 SAM 模型進行精確的食材檢測
- 🍳 智能食譜生成：基於檢測到的食材自動生成合適的食譜
- 👤 個人化推薦：考慮用戶的飲食偏好、烹飪技能和健康目標
- 📊 使用者分析：追蹤並分析使用者的食譜互動記錄
- 🖥️ 友善界面：直觀的網頁介面，支援多種操作功能

## 系統架構

### 核心模組
- `core/`: 核心數據模型和工具類
  - `data_models.py`: 數據結構定義
  - `exceptions.py`: 自定義異常類
  - `utils.py`: 通用工具函數

### 服務層
- `services/`: 核心業務邏輯實現
  - `detector.py`: 食材檢測服務
  - `llm_processor.py`: LLM 處理和食譜生成
  - `recipe_searcher.py`: 食譜搜索和推薦引擎

### 管理器
- `managers/`: 系統資源管理
  - `cache_manager.py`: Redis 快取管理
  - `gpu_manager.py`: GPU 資源管理
  - `system_manager.py`: 系統整體管理
  - `user_manager.py`: 用戶數據管理

### 使用者界面
- `ui/`: 前端介面組件
  - `components.py`: UI 組件定義
  - `event_handler.py`: 事件處理邏輯

### 工具組件
- `utils/`: 輔助工具
  - `logging.py`: 日誌管理
  - `monitoring.py`: 系統監控

## 安裝要求

### 系統需求
- Python 3.12
- CUDA 支援的 GPU（推薦）
- Redis 服務器

### 依賴套件
```bash
pip install -r requirements.txt
```

主要依賴：
- torch
- gradio
- redis
- pandas
- numpy
- llama-cpp-python
- scikit-learn

### 下載必要檔案

1. 下載 LLM 模型
```bash
# 創建模型目錄
mkdir -p project/sam/models

# 下載模型文件
wget https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/blob/main/Meta-Llama-3-8B-Instruct.Q6_K.gguf -O project/sam/models/Meta-Llama-3.1-8B-Instruct-Q6_K.gguf
```

2. 下載食譜數據集（需要 Kaggle 帳號）
```bash
# 安裝 Kaggle CLI
pip install kaggle

# 配置 Kaggle API 憑證
# 將 kaggle.json 放在 ~/.kaggle/ 目錄下
mkdir -p ~/.kaggle
cp path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 下載數據集
kaggle datasets download shuyangli94/food-com-recipes-and-user-interactions

# 解壓縮檔案
unzip food-com-recipes-and-user-interactions.zip

# 移動需要的檔案到專案目錄
mv RAW_recipes.csv RAW_interactions.csv /home/p76131694/FoodSAM-main/
``` 

## 配置說明

系統配置位於 `config/settings.py`，主要包括：

```python
# 路徑配置
base_dir: Path = Path("/home/user/FoodSAM-main/project/sam")
model_path: Path = model_dir / "Meta-Llama-3.1-8B-Instruct-Q6_K.gguf"

# 系統參數
gpu_memory_limit: int = 1000
model_context_size: int = 512

# 服務配置
server_port: int = 7864
server_name: str = "0.0.0.0"
```

## 使用說明

1. 開啟瀏覽器訪問：`http://localhost:7864`

2. 主要功能：
   - 食材檢測與食譜生成
   - 用戶設定管理
   - 歷史記錄查看

3. 使用流程：
   - 上傳食材圖片
   - 系統自動識別食材
   - 生成食譜建議
   - 提供評分反饋

## 系統監控

系統提供完整的監控功能：
- CPU/GPU 使用率監控
- 記憶體使用追蹤
- 性能指標統計
- 錯誤日誌記錄

## 開發指南

### 新增功能
1. 在相應模組中實現功能
2. 更新單元測試
3. 遵循項目代碼規範

### 代碼風格
- 使用類型提示
- 添加適當的文檔字串
- 保持代碼簡潔可讀

## 故障排除

常見問題：
1. GPU 記憶體不足
   - 檢查 `gpu_memory_limit` 設置
   - 關閉其他 GPU 程序

2. Redis 連接失敗
   - 確認 Redis 服務運行狀態
   - 檢查連接配置

3. 模型載入失敗
   - 驗證模型檔案路徑
   - 檢查 CUDA 環境

## License

MIT License
