
# ui/components.py
import gradio as gr
from typing import Dict
import logging
from ..services import EnhancedFoodDetector

class UIComponents:
    """UI組件管理器"""
    def __init__(self, detector: EnhancedFoodDetector):
        self.detector = detector
        self.logger = logging.getLogger(__name__)
        self.components = {}

    def create_main_interface(self) -> gr.Blocks:
        """創建主要界面"""
        try:
            with gr.Blocks(
                title="智慧食譜系統--食材好，食才好",
                theme=gr.themes.Soft(
                    primary_hue="blue",
                    secondary_hue="orange",
                ),
                css=self._get_custom_css()
            ) as demo:
                self._create_header()
                
                with gr.Tabs():
                    with gr.Tab("🔍 食材檢測與食譜生成"):
                        self._create_recipe_tab()
                    
                    with gr.Tab("⚙️ 用戶設定"):
                        self._create_profile_tab()
                    
                    with gr.Tab("📊 歷史記錄"):
                        self._create_history_tab()

                self._create_footer()
                self._bind_events()
                
                return demo

        except Exception as e:
            self.logger.error(f"UI creation error: {e}")
            raise

    def _get_custom_css(self) -> str:
        """獲取自定義CSS"""
        return """
            .container { max-width: 1200px; margin: auto; padding: 20px; }
            .section { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 10px 0; }
            .heading { font-size: 1.2em; font-weight: bold; margin-bottom: 15px; }
            #title-section {
                text-align: center;
                padding: 2rem 0;
                margin-bottom: 2rem;
            }
            #title-section h1 {
                font-size: 2.5em;
                margin-bottom: 0.5rem;
                color: #2b3a55;
            }
            #title-section h3 {
                font-size: 1.2em;
                color: #666;
                font-weight: normal;
            }
        """

    def _create_header(self):
        """創建頁頭"""
        gr.HTML("""
            <div id="title-section">
                <h1>🍳 智慧食譜系統--食材好，食才好</h1>
                <h3>使用AI技術，將您的食材轉換成美味的食譜建議</h3>
            </div>
        """)

    def _create_recipe_tab(self):
        """創建食譜生成頁面"""
        with gr.Row():
            with gr.Column(scale=1):
                self.components['user_id'] = gr.Textbox(
                    label="👤 用戶ID",
                    placeholder="請輸入用戶ID"
                )
                self.components['image_input'] = gr.Image(
                    label="📸 上傳食材圖片",
                    type="filepath",
                    height=300
                )
                self.components['detect_btn'] = gr.Button(
                    "🔍 開始檢測",
                    variant="primary"
                )

            with gr.Column(scale=1):
                self.components['ingredients_output'] = gr.Textbox(
                    label="🥗 檢測到的食材",
                    interactive=False,
                    lines=3
                )
                self.components['recipe_output'] = gr.Textbox(
                    label="📝 生成的食譜",
                    interactive=False,
                    lines=15
                )
                with gr.Row():
                    self.components['rating'] = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=0.5,
                        label="⭐ 食譜評分"
                    )
                    self.components['submit_rating'] = gr.Button(
                        "✅ 提交評分",
                        variant="secondary"
                    )
                self.components['feedback'] = gr.Textbox(
                    label="💬 反饋結果",
                    interactive=False
                )

    def _create_profile_tab(self):
        """創建用戶配置頁面"""
        with gr.Column():
            gr.Markdown("### 👤 基本信息")
            self.components['profile_user_id'] = gr.Textbox(
                label="用戶ID",
                placeholder="請輸入用戶ID"
            )
            
            gr.Markdown("### 🍽️ 飲食偏好")
            self.components['dietary_restrictions'] = gr.CheckboxGroup(
                choices=["素食", "無麩質", "無乳糖", "低碳水", "低脂肪"],
                label="飲食限制"
            )
            self.components['preferred_cuisine'] = gr.Dropdown(
                choices=["中式", "日式", "韓式", "義式", "美式"],
                multiselect=True,
                label="偏好料理類型"
            )
            
            gr.Markdown("### 👨‍🍳 烹飪技能")
            self.components['cooking_skill'] = gr.Slider(
                minimum=1,
                maximum=5,
                value=3,
                step=1,
                label="烹飪技能等級"
            )
            self.components['equipment'] = gr.CheckboxGroup(
                choices=["烤箱", "微波爐", "電鍋", "氣炸鍋", "攪拌機"],
                label="可用設備"
            )
            
            gr.Markdown("### 🎯 健康目標")
            self.components['health_goals'] = gr.CheckboxGroup(
                choices=["減重", "增肌", "營養均衡", "控制血糖"],
                label="健康目標"
            )
            
            self.components['save_btn'] = gr.Button(
                "💾 保存設定",
                variant="primary"
            )
            self.components['profile_status'] = gr.Textbox(
                label="設定狀態",
                interactive=False
            )

    def _create_history_tab(self):
        """創建歷史記錄頁面"""
        with gr.Column():
            with gr.Row():
                self.components['history_user_id'] = gr.Textbox(
                    label="👤 用戶ID", 
                    placeholder="請輸入用戶ID查看歷史記錄",
                    scale=3
                )
                self.components['load_btn'] = gr.Button(
                    "📂 載入歷史",
                    variant="primary",
                    scale=1
                )
            
            with gr.Row():
                with gr.Column(scale=2):
                    self.components['recipe_history'] = gr.Dataframe(
                        headers=["日期", "食譜", "評分"],
                        label="📜 食譜歷史",
                        type="array"
                    )
                with gr.Column(scale=1):
                    self.components['recipe_stats'] = gr.JSON(
                        label="📊 統計資訊"
                    )

    def _create_footer(self):
        """創建頁腳"""
        gr.HTML("""
            <div style="text-align: center; padding: 2rem 0; margin-top: 2rem;">
                <h3>💡 使用提示</h3>
                <p>- 上傳清晰的食材圖片以獲得最佳識別效果</p>
                <p>- 確保填寫正確的用戶ID以保存您的偏好設置</p>
                <p>- 評分和反饋將幫助系統提供更好的推薦</p>
            </div>
        """)

    def _bind_events(self):
        """綁定事件處理"""
        self.components['detect_btn'].click(
            fn=self.detector.detect_ingredients,
            inputs=[self.components['image_input']],
            outputs=[
                self.components['ingredients_output'],
                self.components['recipe_output']
            ]
        )
        
        self.components['submit_rating'].click(
            fn=self.detector.handle_rating_submission,
            inputs=[
                self.components['user_id'],
                self.components['rating']
            ],
            outputs=[self.components['feedback']]
        )
        
        self.components['save_btn'].click(
            fn=self.detector.handle_profile_update,
            inputs=[
                self.components['profile_user_id'],
                self.components['dietary_restrictions'],
                self.components['cooking_skill'],
                self.components['preferred_cuisine'],
                self.components['health_goals'],
                self.components['equipment']
            ],
            outputs=[self.components['profile_status']]
        )
        
        self.components['load_btn'].click(
            fn=self.detector.handle_history_load,
            inputs=[self.components['history_user_id']],
            outputs=[
                self.components['recipe_history'],
                self.components['recipe_stats']
            ]
        )
