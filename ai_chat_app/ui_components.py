"""
ui_components.py
----------------
คลาสสำหรับสร้างชิ้นส่วนหน้าจอ (UI Components) ที่ใช้ซ้ำๆ 
เช่น กล่องข้อความแชท เพื่อแยกโค้ดส่วนแสดงผลออกจากตรรกะหลัก
"""

import os
from typing import Optional
from nicegui import ui
from ai_chat_app.constants import ACCENT_COLORS

class UIComponents:
    
    @staticmethod
    def get_accent_classes(settings: dict) -> dict:
        """ดึงคลาสสีหลักที่เลือกมาใช้งาน"""
        color_name = settings.get("accent_color", "Green")
        return ACCENT_COLORS.get(color_name, ACCENT_COLORS["Green"])

    @staticmethod
    def render_bubble(container, role: str, content: str, image_path: Optional[str] = None, settings: dict = {}):
        """วาดกล่องข้อความ (Bubble) ลงในหน้าจอ"""
        is_user = (role == "user")
        accent = UIComponents.get_accent_classes(settings)
        
        with container:
            if is_user:
                # กล่องข้อความของผู้ใช้ (ชิดขวา, มีสีพื้นหลัง)
                with ui.row().classes("w-full max-w-3xl mx-auto py-4 flex justify-end px-4"):
                    with ui.column().classes(f"max-w-[75%] rounded-3xl px-5 py-3 text-white {accent['bg']} bg-opacity-90"):
                        if image_path and os.path.exists(image_path):
                            ui.image(image_path).classes("max-w-[250px] rounded-lg mb-3 shadow-sm border border-white/20")
                        ui.markdown(content).classes("text-[1rem] leading-relaxed break-words")
            else:
                # กล่องข้อความของ AI (ชิดซ้าย, พื้นหลังใส, มีรูปไอคอน)
                with ui.row().classes("w-full max-w-3xl mx-auto py-6 flex justify-start px-4 gap-4"):
                    with ui.element('div').classes("w-8 h-8 rounded-full flex items-center justify-center border border-[#424242] text-[#ECECEC] flex-shrink-0 bg-transparent"):
                        ui.icon("auto_awesome").classes("text-[1rem]")

                    with ui.column().classes("flex-1 min-w-0 pt-0.5"):
                        if image_path and os.path.exists(image_path):
                            ui.image(image_path).classes("max-w-[300px] rounded-lg mb-4 shadow-sm border border-[#424242]")
                        ui.markdown(content).classes("text-[1rem] leading-7 text-[#ECECEC] break-words prose prose-invert max-w-none")
