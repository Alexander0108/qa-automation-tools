# Marketing QA Automation Suite

A professional toolkit for iGaming marketing operations to validate multilingual campaigns across Customer.io and OneSignal.

## 1. Tools Overview

### 🤖 AI Text & Localization Validator (clickup_customer_io_text_check.py) — v20.6
* **Engine:** OpenAI Multi-model support (GPT-5-mini / GPT-4o).
* **Function:** Intelligent audit of copywriter work vs Technical Requirements.
* **Advanced Features (New):**
    * **Source of Truth (EN):** Automatically uses the English localization (`{% when "en" %}`) as the master reference to cross-check all 8+ other languages (DE, ES, FR, IT, etc.) for data consistency.
    * **Smart HTML Validation:** Strict monitoring of `<strong>` and `<span>` tag placement to prevent layout breakage in CRM templates.
    * **iGaming Snippet Check:** Ensures critical data (Min.dep, Wager, Max.win) uses correct system snippets (e.g., `{{snippets['10_EUR']}}`) instead of plain text.
    * **Urgency Audit:** Validates if Preheaders meet the "urgency/scarcity" requirements from ClickUp.

### Customer.io HTML Integrity Checker (customer_io_check.py)
* **Function:** Technical validation of HTML source code vs ClickUp data.
* **Validation:** Liquid syntax (case/when blocks) and multi-language stack integrity.

### OneSignal Push Validator (onesignal_validator.py)
* **Function:** Automated verification of push notification payloads.
* **Validation:** Title, Body, and URL matching across 18+ languages against Google Sheets data.

## 2. Setup & Installation

### Requirements
* Python 3.10+
* Libraries: `pyperclip`, `python-dotenv`, `openai`

### Configuration
1. Install dependencies:
   `pip install pyperclip python-dotenv openai`
2. Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   MODEL_NAME=gpt-5-mini

## 3. Security Note
* All tools operate via local clipboard integration for data privacy.