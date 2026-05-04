"""
main.py
-------
แอปพลิเคชันแชท AI รองรับหลายโมเดล (AI Multi-Model Chat Application)
เป็นไฟล์หลัก (Entry Point) ที่ใช้เรียกคอมโพเนนต์และโมดูลย่อยมาประกอบร่างเป็นแอป
"""

import os
from typing import Optional

from nicegui import ui, events, app

import sys as _sys
import pathlib as _pathlib

# เพิ่มโฟลเดอร์หลักเข้าไปใน sys.path เพื่อให้สามารถโหลดโมดูลภายในได้
_sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))

from ai_chat_app.api_handler import APIHandler
from ai_chat_app.storage_manager import StorageManager
from ai_chat_app.constants import MODELS, CUSTOM_CSS
from ai_chat_app.ui_components import UIComponents
from ai_chat_app.settings_ui import SettingsUI

class ChatApplication:
    def __init__(self):
        # สร้างอินสแตนซ์สำหรับจัดการ API และระบบจัดเก็บข้อมูล
        self.__api = APIHandler()
        self.__storage = StorageManager()
        
        # ตั้งค่าสถานะเริ่มต้นของแอปพลิเคชัน (ถูกซ่อนด้วย Double Underscore)
        self.__current_session_id: str = self.__storage.generate_session_id()
        self.__attached_image_path: Optional[str] = None
        self.__chat_messages: list[dict] = []
        self.__settings: dict = {}
        
        # ตัวแปรสำหรับอ้างอิง UI element
        self.__refs = {
            "chat_col": None, "session_list_col": None, "thinking": None, 
            "scroll": None, "file_chip": None, "empty_state": None,
            "text_input": None, "send_btn": None, "upload_el": None
        }

    def __clear_attachment(self):
        """ล้างรูปภาพที่แนบไว้"""
        self.__attached_image_path = None
        self.__refs["file_chip"].clear()
        self.__refs["file_chip"].set_visibility(False)

    async def __render_session_list(self):
        """แสดงรายการแชทที่เคยคุยมาทั้งหมดที่แถบด้านซ้าย"""
        col = self.__refs["session_list_col"]
        col.clear()
        sessions = await self.__storage.load_all_sessions()
        
        # จัดเรียงจากอัพเดทล่าสุดไปเก่าสุด
        sorted_sessions = sorted(sessions.items(), key=lambda x: x[1].get("updated_at", ""), reverse=True)

        with col:
            for sid, data in sorted_sessions:
                title = data.get("title", "New Chat")
                is_active = (sid == self.__current_session_id)
                bg_class = "bg-[#212121]" if is_active else "bg-transparent hover:bg-[#212121]"
                
                # สร้างส่วนแสดงแต่ละแชท
                with ui.row().classes(f"w-full px-3 py-2 rounded-lg cursor-pointer transition-colors items-center justify-between group {bg_class}").on("click", lambda e, sid=sid: self.__switch_session(sid)):
                    ui.label(title).classes("truncate text-[0.9rem] text-[#ECECEC] flex-1 mr-2")
                    ui.icon("delete_outline").classes("text-[#B4B4B4] hover:text-[#ECECEC] opacity-0 group-hover:opacity-100 transition-opacity text-[1.1rem]").on("click.stop", lambda e, sid=sid: self.__delete_session_handler(sid))

    async def __switch_session(self, sid: str):
        """เปลี่ยนหน้าไปยังแชทเก่าที่เลือก"""
        self.__current_session_id = sid
        self.__clear_attachment()
        
        self.__chat_messages = await self.__storage.load_session(sid)
        
        chat_col = self.__refs["chat_col"]
        chat_col.clear()
        
        if len(self.__chat_messages) == 0:
            self.__refs["empty_state"].set_visibility(True)
        else:
            self.__refs["empty_state"].set_visibility(False)
            with chat_col:
                for msg in self.__chat_messages:
                    UIComponents.render_bubble(chat_col, msg["role"], msg["content"], msg.get("image_path"), self.__settings)
                    
        await self.__render_session_list()
        
        # เลื่อนหน้าจอลงไปข้างล่างสุดเมื่อเปิดแชทเก่าขึ้นมา
        ui.timer(0.1, lambda: self.__refs["scroll"].scroll_to(percent=1.0), once=True)

    async def __delete_session_handler(self, sid: str):
        """ลบแชทที่เลือก"""
        await self.__storage.delete_session(sid)
        if self.__current_session_id == sid:
            await self.__do_new_chat()
        else:
            await self.__render_session_list()

    async def __do_new_chat(self):
        """สร้างหน้าแชทใหม่"""
        self.__current_session_id = self.__storage.generate_session_id()
        self.__chat_messages = []
        self.__clear_attachment()
        
        self.__refs["chat_col"].clear()
        self.__refs["empty_state"].set_visibility(True)
        await self.__render_session_list()

    async def __do_send(self):
        """ส่งข้อความจากช่องกรอกไปยัง AI"""
        text_input = self.__refs["text_input"]
        text = text_input.value.strip() if text_input.value else ""
        if not text:
            return

        image_path = self.__attached_image_path
        self.__refs["empty_state"].set_visibility(False)

        # 1. แสดงกล่องข้อความของผู้ใช้ทันที
        UIComponents.render_bubble(self.__refs["chat_col"], "user", text, image_path, self.__settings)
        
        # 2. บันทึกข้อความลงไฟล์เก็บประวัติและตัวแปร
        await self.__storage.save_message(self.__current_session_id, "user", text, image_path)
        self.__chat_messages.append({"role": "user", "content": self.__api.format_payload(text, image_path)})
        
        # 3. ล้างช่องกรอกและรูปภาพเตรียมรอรอบถัดไป
        text_input.value = ""
        self.__clear_attachment()
        ui.timer(0.1, lambda: self.__refs["scroll"].scroll_to(percent=1.0), once=True)
        await self.__render_session_list()

        # 4. ดึงข้อมูลโมเดลและการเชื่อมต่อปัจจุบัน
        settings_live = self.__storage.load_settings_sync()
        current_model_name = settings_live["current_model"]
        model_info = MODELS[current_model_name]
        provider = settings_live["providers"][model_info["provider"]]
        
        self.__refs["send_btn"].disable()
        self.__refs["thinking"].set_visibility(True)
        
        # 5. ใส่ข้อมูลส่วนตัว (Personalization) เพื่อให้ AI รู้จักผู้ใช้
        payload = []
        p = settings_live.get("personalization", {})
        if p.get("user_name") or p.get("about_user"):
            sys_msg = "You are a helpful AI assistant. "
            if p.get("user_name"): 
                sys_msg += f"The user's name is {p['user_name']}. "
            if p.get("about_user"): 
                sys_msg += f"Here is some information about the user: {p['about_user']}. "
            payload.append({"role": "system", "content": sys_msg})
            
        payload.extend(self.__chat_messages)

        try:
            # 6. ส่งข้อมูลไปที่เซิร์ฟเวอร์ AI
            ai_text = await self.__api.send_message(
                payload, provider["base_url"], provider["api_key"], model_info["id"]
            )
        except Exception as e:
            ui.notify(str(e), type="negative", position="top", timeout=5000)
            ai_text = None
        finally:
            # ไม่ว่าจะสำเร็จหรือเกิด Error ก็ต้องเปิดปุ่มส่งข้อความใหม่
            self.__refs["send_btn"].enable()
            self.__refs["thinking"].set_visibility(False)

        if ai_text:
            # 7. แสดงและบันทึกกล่องข้อความจาก AI
            UIComponents.render_bubble(self.__refs["chat_col"], "assistant", ai_text, settings=self.__settings)
            await self.__storage.save_message(self.__current_session_id, "assistant", ai_text)
            self.__chat_messages.append({"role": "assistant", "content": ai_text})

        ui.timer(0.1, lambda: self.__refs["scroll"].scroll_to(percent=1.0), once=True)

    async def build_ui(self):
        """สร้างโครงสร้างหน้าต่างแอปพลิเคชันทั้งหมด"""
        # เตรียมค่าเริ่มต้น
        self.__settings = self.__storage.load_settings_sync()
        if "current_model" not in self.__settings or self.__settings["current_model"] not in MODELS:
            self.__settings["current_model"] = list(MODELS.keys())[0]

        if "personalization" not in self.__settings:
            self.__settings["personalization"] = {"user_name": "", "about_user": ""}

        ui.add_head_html('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">')
        ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")

        # โหลดออบเจกต์หน้าต่างตั้งค่าจาก SettingsUI
        settings_ui = SettingsUI(self.__storage, self.__settings)
        settings_ui.build_dialog()

        # สร้างเลย์เอาต์หลักแบบเต็มจอ
        with ui.row().classes("w-screen h-screen overflow-hidden bg-[#212121] gap-0 m-0 p-0 relative"):

            # -----------------------------------------------------
            # แถบเมนูด้านซ้าย (Sidebar)
            # -----------------------------------------------------
            with ui.column().classes("w-[260px] h-full bg-[#171717] flex flex-col p-3 z-20"):
                
                # ปุ่มเริ่มแชทใหม่
                with ui.row().classes("w-full items-center justify-between mb-6 cursor-pointer hover:bg-[#212121] px-3 py-2 rounded-lg transition-colors group").on("click", lambda: self.__do_new_chat()):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("edit_square").classes("text-lg group-hover:text-[#ECECEC] transition-colors")
                        ui.label("New chat").classes("font-medium text-[0.9rem]")
                
                # แสดงรายการแชทที่ผ่านมา
                ui.label("Recents").classes("px-3 text-[0.75rem] font-semibold text-[#B4B4B4] mb-1")
                
                self.__refs["session_list_col"] = ui.column().classes("w-full flex-1 overflow-y-auto gap-0")
                
                # ปุ่มตั้งค่าแอปพลิเคชัน (ตั้งค่าชื่อผู้ใช้, API)
                with ui.column().classes("w-full mt-auto pt-2"):
                    with ui.row().classes("w-full px-3 py-3 rounded-lg items-center gap-3 cursor-pointer transition-colors text-[#ECECEC] hover:bg-[#212121]").on("click", settings_ui.open):
                        with ui.element('div').classes("w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-r from-gray-500 to-gray-400 text-white font-bold text-xs"):
                            uname = self.__settings.get("personalization", {}).get("user_name", "")
                            ui.label(uname[0].upper() if uname else "ME")
                        ui.label("Settings").classes("font-medium text-[0.95rem]")

            # -----------------------------------------------------
            # หน้าต่างแชทหลักด้านขวา
            # -----------------------------------------------------
            with ui.column().classes("flex-1 h-full relative flex flex-col"):
                
                # แถบเลือกโมเดลด้านบน
                with ui.row().classes("w-full h-14 items-center px-4 absolute top-0 z-20 bg-gradient-to-b from-[#212121] to-transparent pt-2"):
                    
                    async def change_model(e):
                        self.__settings["current_model"] = e.value
                        await self.__storage.save_settings(self.__settings)

                    ui.select(
                        options=list(MODELS.keys()), 
                        value=self.__settings["current_model"],
                        on_change=change_model
                    ).classes("settings-input w-[240px] text-lg font-semibold").props("dense borderless")

                # พื้นที่แสดงข้อความ (เลื่อนหน้าจอได้)
                self.__refs["scroll"] = ui.scroll_area().classes("w-full flex-1 pt-16 pb-[160px]")
                with self.__refs["scroll"]:
                    
                    # หน้าจอว่างเปล่าตอนเริ่มต้นแชทใหม่
                    self.__refs["empty_state"] = ui.column().classes("w-full h-[65vh] items-center justify-center")
                    with self.__refs["empty_state"]:
                        ui.label("Where should we begin?").classes("text-3xl font-semibold text-[#ECECEC] mb-8")

                    # พื้นที่วางกล่องข้อความเรียงกัน
                    self.__refs["chat_col"] = ui.column().classes("w-full gap-0")

                # แถบกรอกข้อความด้านล่าง (ลอยอยู่เหนือหน้าจอ)
                with ui.column().classes("absolute bottom-0 w-full bg-gradient-to-t from-[#212121] via-[#212121] to-transparent pt-10 pb-8 px-4 z-10 pointer-events-none"):
                    
                    # ไอคอนโหลดข้อมูล (Thinking...)
                    thinking_container = ui.row().classes("w-full max-w-3xl mx-auto mb-2 justify-center pointer-events-auto")
                    with thinking_container:
                        self.__refs["thinking"] = ui.row().classes("items-center gap-2 px-3 py-1.5 rounded-full bg-[#2F2F2F] text-[#B4B4B4] text-xs font-medium shadow-md")
                        with self.__refs["thinking"]:
                            ui.spinner('dots', size='sm', color='currentColor')
                            ui.label("Thinking...")
                        self.__refs["thinking"].set_visibility(False)

                    # กล่องแสดงไฟล์ภาพที่ถูกแนบมา
                    self.__refs["file_chip"] = ui.row().classes("w-full max-w-3xl mx-auto mb-2 px-4 transition-all pointer-events-auto")
                    self.__refs["file_chip"].set_visibility(False)

                    # ช่องกรอกข้อความและปุ่มคำสั่ง
                    with ui.row().classes("w-full max-w-3xl mx-auto bg-[#2F2F2F] rounded-[24px] items-end px-3 py-3 shadow-lg pointer-events-auto"):
                        
                        def on_upload(e: events.UploadEventArguments):
                            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
                            os.makedirs(upload_dir, exist_ok=True)
                            dest = os.path.join(upload_dir, e.file.name)
                            ui.timer(0, lambda: handle_async_upload(e.file, dest), once=True)

                        async def handle_async_upload(file_obj, dest: str):
                            await file_obj.save(dest)
                            self.__attached_image_path = dest
                            fc = self.__refs["file_chip"]
                            fc.clear()
                            with fc:
                                with ui.row().classes("bg-[#424242] text-[#ECECEC] px-4 py-2 rounded-xl flex items-center gap-2 text-sm shadow-md"):
                                    ui.icon("image").classes("text-sm")
                                    ui.label(os.path.basename(dest)).classes("truncate max-w-[150px]")
                                    ui.icon("close").classes("text-sm cursor-pointer hover:text-white transition-colors").on("click", self.__clear_attachment)
                            fc.set_visibility(True)

                        self.__refs["upload_el"] = ui.upload(on_upload=on_upload, auto_upload=True).props('accept=".png,.jpg,.jpeg"').classes("hidden-upload")

                        accent = UIComponents.get_accent_classes(self.__settings)
                        
                        # ปุ่มแนบไฟล์รูปภาพ (+)
                        # ใช้ js_handler แทนการเรียกผ่านฝั่งเซิร์ฟเวอร์ เพื่อแก้ปัญหา Safari บล็อกการทำงาน
                        # ทริกเกอร์ <input type="file"> โดยตรงเพื่อให้ทำงานได้ 100% บนทุกเบราว์เซอร์
                        attach_btn = ui.button(icon="add").classes(
                            f"w-8 h-8 rounded-full text-white transition-colors mb-1 mr-2 {accent['bg']} {accent['hover']}"
                        ).props("flat dense").on("click", js_handler="() => { const input = document.querySelector('.hidden-upload input[type=file]'); if (input) input.click(); }")

                        # ช่องกรอกข้อความ
                        self.__refs["text_input"] = ui.textarea(placeholder="Ask anything").classes(
                            "chat-textarea flex-1 mb-1 max-h-[200px] overflow-y-auto"
                        ).props("dense autogrow rows=1")

                        # ปุ่มส่งข้อความ
                        self.__refs["send_btn"] = ui.button(icon="arrow_upward").classes(
                            f"w-8 h-8 rounded-full text-white transition-colors mb-1 ml-2 {accent['bg']} {accent['hover']}"
                        ).props("flat dense")

                    ui.label("AI can make mistakes. Consider verifying important information.").classes("w-full text-center text-[0.7rem] text-[#B4B4B4] mt-3 pointer-events-auto")

        # เริ่มโหลดข้อมูลและตั้งค่าปุ่ม
        await self.__switch_session(self.__current_session_id)

        self.__refs["send_btn"].on("click", self.__do_send)
        # ตั้งค่าให้กด Enter เพื่อส่งข้อความได้ (แต่ Shift+Enter คือขึ้นบรรทัดใหม่)
        self.__refs["text_input"].on("keydown", self.__do_send, js_handler="(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); emit(); } }")

@ui.page("/")
async def main_page() -> None:
    app_instance = ChatApplication()
    await app_instance.build_ui()

if __name__ in ("__main__", "__mp_main__"):
    ui.run(title="AI Assistant", dark=True, favicon="🚀", port=8080, reload=False, show=True)
