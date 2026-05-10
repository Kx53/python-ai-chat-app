"""
settings_ui.py
--------------
คลาสสำหรับจัดการหน้าต่างตั้งค่าของแอปพลิเคชัน (Settings Dialog)
"""

from nicegui import ui
from ai_chat_app.constants import ACCENT_COLORS
from ai_chat_app.storage_manager import StorageManager
from ai_chat_app.ui_components import UIComponents

class SettingsUI:
    def __init__(self, storage_manager: StorageManager, settings: dict):
        self.__storage = storage_manager
        self.__settings = settings
        self.dialog = None

    def build_dialog(self):
        """สร้างหน้าต่างตั้งค่า"""
        with ui.dialog() as settings_dialog, ui.card().classes("w-[850px] max-w-[95vw] h-[650px] bg-[#2F2F2F] text-[#ECECEC] flex flex-row rounded-2xl overflow-hidden"):
            active_tab = {"name": "General"}

            with ui.row().classes("w-full h-full flex-nowrap m-0 p-0"):
                # แถบซ้าย (แท็บต่างๆ)
                with ui.column().classes("w-[240px] bg-[#212121] h-full py-4 px-3 border-r border-[#424242] gap-1"):
                    ui.label("Settings").classes("text-xl font-semibold mb-4 px-3")
                    
                    @ui.refreshable
                    def render_tabs():
                        tabs = [
                            ("General", "settings"),
                            ("API Providers", "api"),
                            ("Personalization", "person")
                        ]
                        for name, icon in tabs:
                            is_active = (active_tab["name"] == name)
                            bg_class = "bg-[#2F2F2F] font-semibold" if is_active else "bg-transparent hover:bg-[#2F2F2F]"
                            
                            def make_tab_handler(tab_name):
                                def handler(event):
                                    active_tab["name"] = tab_name
                                    render_tabs.refresh()
                                    render_tab_content.refresh()
                                return handler
                            
                            with ui.row().classes(f"w-full px-3 py-2.5 rounded-lg items-center gap-3 cursor-pointer transition-colors {bg_class}").on("click", make_tab_handler(name)):
                                ui.icon(icon).classes("text-[1.1rem]" + (" text-[#ECECEC]" if is_active else " text-[#B4B4B4]"))
                                ui.label(name).classes("text-[0.95rem]" + (" text-[#ECECEC]" if is_active else " text-[#B4B4B4]"))

                    render_tabs()

                # พื้นที่หลักตรงกลางแสดงเนื้อหาของการตั้งค่า
                with ui.column().classes("flex-1 h-full relative"):
                    with ui.row().classes("w-full justify-end p-4 absolute top-0 right-0 z-10"):
                        ui.icon("close").classes("text-2xl text-[#B4B4B4] hover:text-[#ECECEC] cursor-pointer").on("click", settings_dialog.close)
                    
                    @ui.refreshable
                    def render_tab_content():
                        with ui.column().classes("w-full h-full p-8 overflow-y-auto"):
                            ui.label(active_tab["name"]).classes("text-2xl font-semibold border-b border-[#424242] pb-4 mb-6 w-full")

                            if active_tab["name"] == "General":
                                ui.label("Accent color").classes("text-[1rem] font-semibold mb-4")
                                
                                # วงกลมสำหรับเลือกสี
                                with ui.row().classes("gap-4 items-center mb-8"):
                                    current_color = self.__settings.get("accent_color", "Green")
                                    
                                    def make_color_selector(color_name):
                                        def handler(event):
                                            self.__settings["accent_color"] = color_name
                                            render_tab_content.refresh()
                                        return handler

                                    for color_name, color_classes in ACCENT_COLORS.items():
                                        is_selected = (color_name == current_color)
                                        bg_class = color_classes["bg"]
                                        ring_class = "ring-2 ring-offset-2 ring-offset-[#2F2F2F] ring-white" if is_selected else "opacity-70 hover:opacity-100"
                                        
                                        c_el = ui.element('div').classes(f"w-8 h-8 rounded-full cursor-pointer transition-all {bg_class} {ring_class} hover:scale-110")
                                        c_el.on("click", make_color_selector(color_name))
                                            
                            elif active_tab["name"] == "API Providers":
                                ui.label("กำหนดการเชื่อมต่อกับ AI Provider ต่างๆ").classes("text-[#B4B4B4] mb-6")
                                
                                def make_updater(provider, key):
                                    def handler(event):
                                        if "providers" not in self.__settings: 
                                            self.__settings["providers"] = {}
                                        if provider not in self.__settings["providers"]: 
                                            self.__settings["providers"][provider] = {}
                                        self.__settings["providers"][provider][key] = event.value
                                    return handler
                                
                                # LM Studio
                                ui.label("LM Studio (Local AI)").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.input("Base URL", value=self.__settings["providers"]["lm_studio"]["base_url"], on_change=make_updater("lm_studio", "base_url")).classes("settings-input w-full mb-2")
                                ui.input("API Key (Optional)", value=self.__settings["providers"]["lm_studio"]["api_key"], password=True, on_change=make_updater("lm_studio", "api_key")).classes("settings-input w-full mb-6")

                                # OpenAI
                                ui.label("OpenAI").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.input("Base URL", value=self.__settings["providers"]["openai"]["base_url"], on_change=make_updater("openai", "base_url")).classes("settings-input w-full mb-2")
                                ui.input("API Key", value=self.__settings["providers"]["openai"]["api_key"], password=True, on_change=make_updater("openai", "api_key")).classes("settings-input w-full mb-6")

                                # Anthropic
                                ui.label("Anthropic (OpenRouter/API)").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.input("Base URL", value=self.__settings["providers"]["anthropic"]["base_url"], on_change=make_updater("anthropic", "base_url")).classes("settings-input w-full mb-2")
                                ui.input("API Key", value=self.__settings["providers"]["anthropic"]["api_key"], password=True, on_change=make_updater("anthropic", "api_key")).classes("settings-input w-full mb-6")

                                # Google Gemini
                                ui.label("Google Gemini (API)").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.input("Base URL", value=self.__settings.get("providers", {}).get("google", {}).get("base_url", ""), on_change=make_updater("google", "base_url")).classes("settings-input w-full mb-2")
                                ui.input("API Key", value=self.__settings.get("providers", {}).get("google", {}).get("api_key", ""), password=True, on_change=make_updater("google", "api_key")).classes("settings-input w-full mb-6")

                            elif active_tab["name"] == "Personalization":
                                ui.label("กำหนดข้อมูลส่วนตัวเพื่อให้ AI ตอบกลับตรงกับคุณมากขึ้น").classes("text-[#B4B4B4] mb-6")
                                
                                def update_personalization(key, value):
                                    if "personalization" not in self.__settings: 
                                        self.__settings["personalization"] = {}
                                    self.__settings["personalization"][key] = value

                                def make_person_updater(key):
                                    def handler(event):
                                        update_personalization(key, event.value)
                                    return handler

                                ui.label("About You").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.input("Your Name / Username", value=self.__settings["personalization"]["user_name"], on_change=make_person_updater("user_name")).classes("settings-input w-full mb-6")
                                
                                ui.label("More about you").classes("text-[1.05rem] font-semibold text-[#ECECEC] mb-2")
                                ui.textarea("Interests, hobbies, or rules for the AI...", value=self.__settings["personalization"]["about_user"], on_change=make_person_updater("about_user")).classes("settings-input w-full mb-6").props("autogrow")

                            # ปุ่มบันทึกและยกเลิกด้านล่าง
                            with ui.row().classes("w-full justify-end p-6 border-t border-[#424242] mt-auto bg-[#2F2F2F]"):
                                async def save_settings_and_reload():
                                    await self.__storage.save_settings(self.__settings)
                                    ui.notify("บันทึกการตั้งค่าเรียบร้อยแล้ว การเปลี่ยนแปลงบางอย่างจะมีผลเมื่อโหลดแอปใหม่", type="positive", position="top")
                                    settings_dialog.close()
                                    ui.navigate.reload()
                                
                                accent = UIComponents.get_accent_classes(self.__settings)
                                ui.button("Cancel", on_click=settings_dialog.close).classes(f"bg-transparent {accent['text']} hover:bg-[#424242] rounded-lg px-4 py-2 mr-2 font-semibold").props("flat")
                                ui.button("Save Changes", on_click=save_settings_and_reload).classes(f"text-white font-semibold rounded-lg px-6 py-2 {accent['bg']} {accent['hover']}").props("flat")

                    render_tab_content()
        self.dialog = settings_dialog
        return settings_dialog

    def open(self):
        """แสดงหน้าต่างการตั้งค่า"""
        if self.dialog:
            self.dialog.open()
