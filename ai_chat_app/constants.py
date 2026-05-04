"""
constants.py
------------
เก็บค่าคงที่ทั้งหมดของแอปพลิเคชัน (เช่น โทนสี, รายชื่อโมเดล AI, และรูปแบบ CSS)
เพื่อแยกข้อมูลออกจากลอจิกโปรแกรม ทำให้แก้ไขได้ง่ายในที่เดียว
"""

# ค่าคงที่สำหรับการตั้งค่าสี
ACCENT_COLORS = {
    "Orange": {"bg": "bg-[#F97316]", "text": "text-[#F97316]", "hover": "hover:bg-[#EA580C]"},
    "Blue": {"bg": "bg-[#3B82F6]", "text": "text-[#3B82F6]", "hover": "hover:bg-[#2563EB]"},
    "Green": {"bg": "bg-[#10A37F]", "text": "text-[#10A37F]", "hover": "hover:bg-[#0E906F]"},
    "Purple": {"bg": "bg-[#8B5CF6]", "text": "text-[#8B5CF6]", "hover": "hover:bg-[#7C3AED]"},
    "Red": {"bg": "bg-[#EF4444]", "text": "text-[#EF4444]", "hover": "hover:bg-[#DC2626]"}
}

# รายชื่อโมเดล AI ที่รองรับ
MODELS = {
    "LM Studio Local AI": {"id": "local-model", "provider": "lm_studio"},
    "GPT-5.5": {"id": "gpt-5.5-2026-04-23", "provider": "openai"},
    "GPT 5.4 mini": {"id": "gpt-5.4-mini-2026-03-17", "provider": "openai"},
    "Claude Sonnet 4.7": {"id": "claude-sonnet-4-6", "provider": "anthropic"},
    "Claude Opus 4.7": {"id": "claude-opus-4-7", "provider": "anthropic"},
    "Gemini 3.1 Pro": {"id": "gemini-3.1-pro-preview", "provider": "google"},
    "Gemini 3.1 Flash": {"id": "gemini-3-flash-preview", "provider": "google"}
}

# รูปแบบ CSS พื้นฐานของแอปพลิเคชัน
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #212121 !important;
    color: #ECECEC !important;
    margin: 0; padding: 0; overflow: hidden;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #424242; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #565656; }

.hidden-upload { position: absolute; width: 0; height: 0; overflow: hidden; opacity: 0; pointer-events: none; }

/* จัดการหน้าต่าง Dialog */
.q-dialog__inner > div {
    border-radius: 16px !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7) !important;
    border: 1px solid #424242 !important;
    padding: 0 !important;
}

/* จัดการช่องข้อความแชท */
.chat-textarea .q-field__control {
    background: transparent !important;
    min-height: 24px !important;
}
.chat-textarea .q-field__control:before, .chat-textarea .q-field__control:after {
    display: none !important;
}
.chat-textarea textarea {
    color: #ECECEC !important;
    padding: 0 !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
}
.chat-textarea .q-field__bottom { display: none !important; }

/* จัดการช่องกรอกข้อมูลในการตั้งค่า */
.settings-input .q-field__control {
    background: #212121 !important;
    border-radius: 8px !important;
    border: 1px solid #424242 !important;
}
.settings-input .q-field--outlined .q-field__control:before { border: none !important; }
.settings-input .q-field__native, .settings-input .q-field__input { color: #ECECEC !important; }
.settings-input .q-icon { color: #B4B4B4 !important; }
"""
