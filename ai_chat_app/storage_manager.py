"""
storage_manager.py
------------------
จัดการการจัดเก็บประวัติการแชทลงในไฟล์บนเครื่อง
โดยแต่ละการแชทจะถูกบันทึกแยกเป็นไฟล์ JSON ในโฟลเดอร์ 'chats'
"""

import asyncio
import json
import os
import uuid
import glob
from datetime import datetime
from typing import Optional

# โฟลเดอร์หลักสำหรับจัดเก็บข้อมูล
STORAGE_DIR = os.path.dirname(__file__)
CHATS_DIR = os.path.join(STORAGE_DIR, "chats")
SETTINGS_FILE = os.path.join(STORAGE_DIR, "settings.json")

# ตรวจสอบและสร้างโฟลเดอร์ chats หากยังไม่มี
os.makedirs(CHATS_DIR, exist_ok=True)

DEFAULT_SETTINGS = {
    "accent_color": "Green",
    "providers": {
        "lm_studio": {"base_url": "http://localhost:1234/v1", "api_key": "lm-studio"},
        "openai": {"base_url": "https://api.openai.com/v1", "api_key": ""},
        "anthropic": {"base_url": "https://openrouter.ai/api/v1", "api_key": ""},
        "google": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "api_key": ""}
    },
    "current_model": "gpt-5.5-nano",
    "personalization": {
        "user_name": "",
        "about_user": ""
    }
}

class StorageManager:
    def __init__(self):
        # กำหนดค่าตัวแปรเริ่มต้น (ซ่อนข้อมูลด้วย Double Underscore)
        self.__chats_dir = CHATS_DIR
        self.__settings_file = SETTINGS_FILE

    def load_settings_sync(self) -> dict:
        """
        โหลดการตั้งค่าแบบทำงานประสานเวลา (Synchronous) สำหรับการเปิดแอปครั้งแรก
        """
        if not os.path.exists(self.__settings_file):
            return DEFAULT_SETTINGS.copy()
        try:
            with open(self.__settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # รวมค่าที่ตั้งไว้ (data) ทับค่าเริ่มต้น
                result = DEFAULT_SETTINGS.copy()
                result.update(data)
                return result
        except (json.JSONDecodeError, OSError):
            return DEFAULT_SETTINGS.copy()

    async def save_settings(self, settings: dict) -> None:
        """บันทึกการตั้งค่าลงไฟล์ (Asynchronous)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__write_file, self.__settings_file, settings)

    async def load_all_sessions(self) -> dict:
        """
        โหลดข้อมูลประวัติแชททั้งหมดจากโฟลเดอร์ 'chats'
        คืนค่ากลับมาเป็น Dictionary ที่มี session_id เป็นกุญแจ
        """
        loop = asyncio.get_event_loop()
        
        def _read_all_files():
            result = {}
            pattern = os.path.join(self.__chats_dir, "*.json")
            for filepath in glob.glob(pattern):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        session_id = os.path.basename(filepath).replace(".json", "")
                        result[session_id] = data
                except (json.JSONDecodeError, OSError):
                    continue
            return result

        sessions = await loop.run_in_executor(None, _read_all_files)
        return sessions

    async def load_session(self, session_id: str) -> list[dict]:
        """โหลดข้อความของแชทจากรหัส session_id"""
        session_file = os.path.join(self.__chats_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            return []
            
        loop = asyncio.get_event_loop()
        try:
            content = await loop.run_in_executor(None, self.__read_file, session_file)
            data = json.loads(content)
            return data.get("messages", [])
        except (json.JSONDecodeError, OSError):
            return []

    async def save_message(self, session_id: str, role: str, content: str, image_path: Optional[str] = None) -> None:
        """
        เพิ่มข้อความใหม่ต่อท้ายไฟล์แชทที่ระบุด้วย session_id
        """
        session_file = os.path.join(self.__chats_dir, f"{session_id}.json")
        loop = asyncio.get_event_loop()
        
        # 1. โหลดข้อมูลแชทเดิม หรือ สร้างโครงสร้างแชทใหม่หากไม่เคยมี
        if os.path.exists(session_file):
            try:
                file_content = await loop.run_in_executor(None, self.__read_file, session_file)
                session_data = json.loads(file_content)
            except (json.JSONDecodeError, OSError):
                session_data = self.__create_empty_session()
        else:
            session_data = self.__create_empty_session()
            
        # 2. เพิ่มข้อความใหม่
        now = datetime.now().isoformat(timespec="seconds")
        session_data["updated_at"] = now
        
        # ตั้งค่าเวลาสร้างหากเพิ่งสร้างแชทใหม่
        if not session_data.get("created_at"):
            session_data["created_at"] = now
            
        session_data["messages"].append(
            {
                "role": role,
                "content": content,
                "image_path": image_path,
                "timestamp": now,
            }
        )
        
        # 3. สร้างชื่อแชทอัตโนมัติหากเป็นข้อความแรกของผู้ใช้
        if role == "user" and len(session_data["messages"]) == 1:
            session_data["title"] = self.__generate_title(content)

        # 4. บันทึกข้อมูลกลับลงไปในไฟล์
        await loop.run_in_executor(None, self.__write_file, session_file, session_data)

    async def delete_session(self, session_id: str) -> None:
        """ลบไฟล์แชทจากรหัส session_id"""
        session_file = os.path.join(self.__chats_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, os.remove, session_file)

    async def clear_all_history(self) -> None:
        """ลบประวัติการแชททั้งหมด (ลบไฟล์ทุกไฟล์ในโฟลเดอร์ chats)"""
        loop = asyncio.get_event_loop()
        def _delete_all():
            pattern = os.path.join(self.__chats_dir, "*.json")
            for filepath in glob.glob(pattern):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
        await loop.run_in_executor(None, _delete_all)

    def generate_session_id(self) -> str:
        """สร้างรหัส session_id ใหม่ (สุ่มตัวอักษรและตัวเลข)"""
        return str(uuid.uuid4())

    # ---------------------------------------------------------------------------
    # ฟังก์ชันตัวช่วยส่วนตัว (Private Helpers)
    # ---------------------------------------------------------------------------

    def __create_empty_session(self) -> dict:
        """สร้างโครงสร้างของแชทว่างเปล่า"""
        return {
            "title": "New Chat",
            "created_at": "",
            "updated_at": "",
            "messages": []
        }

    def __generate_title(self, first_message: str) -> str:
        """สร้างชื่อแชทสั้นๆ จากข้อความแรกของผู้ใช้"""
        title = first_message.strip().split("\n")[0]
        if len(title) > 25:
            return title[:25] + "..."
        return title or "New Chat"

    def __read_file(self, path: str) -> str:
        """อ่านไฟล์ข้อความและส่งคืนเป็น string"""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def __write_file(self, path: str, data: dict) -> None:
        """เขียนข้อมูล dict ลงในไฟล์ JSON"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
