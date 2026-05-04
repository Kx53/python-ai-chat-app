# 🚀 AI Multi-Model Chat Application

> A professional, desktop-grade AI chat application built entirely in Python. Developed as a University Project (10 points).

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![NiceGUI](https://img.shields.io/badge/NiceGUI-Framework-teal.svg)
![uv](https://img.shields.io/badge/uv-Package_Manager-purple.svg)

## ✨ Features

- 🌐 **Multi-Provider Support**: Seamlessly switch between OpenAI, Anthropic (via OpenRouter/API), Google Gemini, and Local AI (LM Studio).
- 👁️ **Vision Capability**: Attach `.jpg` or `.png` files to analyze images with supported AI models.
- 🎨 **Personalization & Theming**: Customize UI accent colors, set system prompts ("About You"), and configure user profiles.
- 💾 **Local Data Persistence**: Chat histories, image attachments, and user settings are securely saved locally on your machine.
- ⚡ **Responsive UI**: A modern 2-column layout (Sidebar + Main Content) with real-time updates and smooth interactions.

## 🛠️ Tech Stack

- **Core**: Python 3.14+
- **Environment & Package Manager**: [uv](https://docs.astral.sh/uv/) (Extremely fast Python package installer)
- **UI Framework**: [NiceGUI](https://nicegui.io/)
- **API Integration**: `openai` (Unified API client for all models)

---

## 📦 Installation & Setup (Using `uv`)

This project uses **`uv`**, an ultra-fast Python package and project manager written in Rust. It makes setting up the project extremely simple.

### 1. Install `uv` (If not already installed)

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd project10points
```

### 3. Install Dependencies
Use `uv sync` to automatically create a virtual environment and install all dependencies listed in the `pyproject.toml` file:

```bash
uv sync
```

### 4. Run the Application
Once synced, you can run the application seamlessly using:

```bash
uv run ai_chat_app/main.py
```

The application will start, and a browser window should automatically open at `http://localhost:8080`.

---

## ⚙️ Configuration & Usage

1. **Accessing Settings**: Click the "Settings" button at the bottom left of the sidebar.
2. **API Keys**: Navigate to the **API Providers** tab to input your API keys for OpenAI, Anthropic, or Google Gemini. Your keys are saved locally.
3. **Local AI (LM Studio)**: If you want to run models completely offline, start your LM Studio local server on port `1234` (Default Base URL: `http://localhost:1234/v1`).
4. **Customization**: Go to the **General** tab to change the app's Accent Color, or the **Personalization** tab to tell the AI your name and interests.

---

## 📁 Project Structure

```text
.
├── ai_chat_app/
│   ├── main.py               # Core application and main layout structure
│   ├── api_handler.py        # Logic for calling AI APIs & formatting payloads
│   ├── storage_manager.py    # Logic for reading/writing chat history and settings
│   ├── constants.py          # Application constants (models, colors, CSS)
│   ├── ui_components.py      # Reusable UI components (e.g., chat bubbles)
│   ├── settings_ui.py        # Settings dialog and user preferences UI
│   ├── settings.json         # Saved user settings (Auto-generated)
│   ├── chats/                # Chat history storage folder (Auto-generated)
│   └── uploads/              # Image uploads folder (Auto-generated)
├── pyproject.toml            # Project dependencies and metadata
└── README.md                 # Project documentation
```

---

*Developed for an Academic Project. Contributions and forks are welcome!*
