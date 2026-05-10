"""
api_handler.py
--------------
จัดการการเชื่อมต่อและส่งข้อความไปยัง AI Provider ต่างๆ
(เช่น LM Studio, OpenRouter, OpenAI) โดยใช้ไลบรารี openai
รองรับการส่งข้อความธรรมดาและการแนบรูปภาพ (Vision)
"""

import base64
import mimetypes
from typing import Optional

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)

class APIHandler:
    def __init__(self):
        # คลาสนี้ใช้สำหรับจัดการ API โดยตรง ยังไม่มีสถานะที่ต้องเก็บไว้เป็นพิเศษ
        pass

    def __create_client(self, base_url: str, api_key: str) -> AsyncOpenAI:
        """
        สร้างออบเจกต์ AsyncOpenAI สำหรับเชื่อมต่อกับ Provider
        """
        return AsyncOpenAI(
            base_url=base_url.rstrip("/"),
            api_key=api_key or "lm-studio",  # สำหรับ LM Studio สามารถใช้ค่าอะไรก็ได้ที่ไม่ใช่ค่าว่าง
        )

    def format_payload(self, text: str, image_path: Optional[str] = None) -> str | list[dict]:
        """
        จัดรูปแบบข้อความที่จะส่งให้ API
        - ถ้ามีแต่ข้อความ จะส่งกลับเป็น string ธรรมดา
        - ถ้ามีรูปภาพ จะแปลงรูปภาพเป็น base64 และส่งเป็น list
        """
        if not image_path:
            return text

        # คาดเดาประเภทของไฟล์รูปภาพ
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
            mime_type = "image/jpeg"

        # เปิดไฟล์ภาพเพื่อแปลงเป็นรหัส base64 ตามกฎ context manager
        with open(image_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode("utf-8")

        return [
            {"type": "text", "text": text},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_data}"},
            },
        ]

    async def send_message(self, messages: list[dict], base_url: str, api_key: str, model: str) -> str:
        """
        ส่งประวัติการแชทไปยัง AI Provider และรับข้อความตอบกลับ
        """
        client = self.__create_client(base_url, api_key)

        # กรองเอาเฉพาะ role และ content ก่อนส่งให้ API โดยใช้ลูป for ธรรมดาเพื่อให้อ่านง่าย
        api_messages = []
        for message in messages:
            if message.get("role") in ("user", "assistant", "system"):
                api_messages.append({"role": message["role"], "content": message["content"]})

        try:
            # ดึงคำตอบจาก AI
            response = await client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=False,
            )
            return response.choices[0].message.content or ""

        except APIConnectionError as error:
            raise ConnectionError(
                f"ไม่สามารถเชื่อมต่อ {base_url} ได้ — "
                "ตรวจสอบว่า LM Studio / OpenRouter เปิดอยู่"
            ) from error

        except AuthenticationError as error:
            raise PermissionError(
                "API Key ไม่ถูกต้อง — กรุณาตรวจสอบ API Key ในหน้าตั้งค่า (Sidebar)"
            ) from error

        except APITimeoutError as error:
            raise TimeoutError(
                "Request หมดเวลา — โมเดลอาจใช้เวลานาน ลองใหม่อีกครั้ง"
            ) from error

        except RateLimitError as error:
            raise RuntimeError(
                "ใช้งาน API เกินจำนวนครั้งที่กำหนด กรุณารอสักครู่แล้วลองใหม่"
            ) from error

        except BadRequestError as error:
            raise ValueError(
                f"คำขอไม่ถูกต้อง หรือโมเดลไม่รองรับข้อมูลนี้: {error}"
            ) from error

        except APIError as error:
            raise RuntimeError(f"เกิดข้อผิดพลาดจาก API Provider: {error}") from error
