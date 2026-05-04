### 📋 Master Prompt for AI Agent (Antigravity)

**[Project Objective]**
Develop an "AI Multi-Model Chat Application" for a university project (10 points). The application must be a desktop-grade UI built entirely in Python. It allows users to chat with multiple AI providers (Local LM Studio, OpenRouter, OpenAI) using a single API interface, supports image attachments (Vision), and persistently saves chat history locally.

**[Tech Stack & Environment]**

- **Python Version:** 3.14+
- **Environment Manager:** `uv`
- **UI Framework:** `NiceGUI` (Strictly use ONLY this framework, NO tkinter/customtkinter).
- **Dependencies:** `openai` (for unified API calls), `python-dotenv` (optional for secrets).
- **Standard Libraries:** `json`, `os`, `base64`, `asyncio`.

**[File Structure]**

```text
ai_chat_app/
├── main.py               # Core application and main layout structure
├── api_handler.py        # Logic for calling OpenAI API & formatting payloads
├── storage_manager.py    # Logic for reading/writing chat history and settings
├── constants.py          # Application constants (models, colors, CSS)
├── ui_components.py      # Reusable UI components (e.g., chat bubbles)
├── settings_ui.py        # Settings dialog and user preferences UI
├── settings.json         # Saved user settings
├── chats/                # Auto-generated chat history storage folder
└── uploads/              # Auto-generated image uploads folder
```

**[UI/UX Layout Specifications]**
Implement a 2-column layout with a Settings Dialog (Sidebar + Main Content):

1. **Sidebar (Left, distinct background color):**
   - **Button:** "New chat" (clears current screen and starts a new session).
   - **Recents List:** Displays past chat sessions.
   - **Settings Button (Bottom):** Opens the Settings Dialog.
2. **Main Chat Area (Right, flex-1):**
   - **Top Header:** Dropdown to select the current AI model.
   - **Scrollable Chat Container:** Displays messages. User messages aligned right, AI messages aligned left.
   - **Bottom Input Row (Sticky):**
     - **Attachment Button:** Opens file picker to select `.png` or `.jpg`. Shows selected filename chip if attached.
     - **Text Input Field:** Multiline capable, expands slightly with text. Enter key to send, Shift+Enter for new line.
     - **Send Button:** Triggers the send function. Show "Thinking..." state during API wait.
3. **Settings Dialog (Modal):**
   - **Tabbed Layout:** General (Accent color), API Providers (Base URL, API Key for multiple providers), and Personalization (User info).

**[Core Logic & Behaviors]**

1. **Unified API Call (api_handler.py):**
   - Instantiate the OpenAI client dynamically using the `Base URL` and `API Key` from user settings.
   - **Payload Formatting:**
     - If NO image is attached: Send standard `{"role": "user", "content": "text"}`.
     - If an image IS attached: Encode image to Base64. Send multipart content: `{"role": "user", "content": [{"type": "text", "text": "text"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_string}"}}]}`.
2. **Data Persistence (storage_manager.py):**
   - **On Startup:** Load settings and session list. Render past chats in the sidebar.
   - **On Send/Receive:** Save individual chat sessions as separate JSON files inside the `chats/` directory. Store image references as local file paths in the `uploads/` directory to prevent massive files. Save user settings in `settings.json`.
3. **Error Handling (Crucial):**
   - Wrap API calls in `try-except` blocks.
   - Catch connection timeouts, invalid API keys, and missing local servers.
   - Display errors via UI notifications/snackbars (do NOT crash the app).

**[Coding Standards for AI]**

- Use `async/await` for API calls and file operations to prevent UI freezing.
- Provide clear Docstrings and Type Hinting (`str`, `List[Dict]`, etc.) for all functions.
- Keep the UI code declarative and separated from the API/Storage business logic.
- Ensure the code runs flawlessly via `uv run main.py`.

---
