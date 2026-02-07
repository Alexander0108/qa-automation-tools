import os
import re
import pyperclip
from dotenv import load_dotenv

# ==========================================================
# CONFIGURATION
# ==========================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

# CHOOSE YOUR MODEL:
# "gpt-4o-mini" - Fast & cheap ($0.0004 / request)
# "gpt-4o"      - Ultra-precise & Smart ($0.007 / request)
MODEL_NAME = "gpt-4o-mini" 

# ==========================================================
# CORE LOGIC
# ==========================================================

def clean_content(text: str) -> str:
    """Removes CRM technical noise, image links, and table headers."""
    text = re.sub(r'https?://\S*(?:png|jpg|jpeg|gif|svg|webp)\S*', '', text)
    lines = text.split('\n')
    ignore_list = ['element', 'content', 'design', 'https']
    cleaned = [line.strip() for line in lines if line.strip() and not any(x in line.lower() for x in ignore_list)]
    return "\n".join(cleaned)

def ai_validator(tz_text: str, copy_text: str) -> str:
    """AI engine to validate localization, style, and syntax."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "❌ ERROR: OPENAI_API_KEY not found in .env file!"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        system_msg = """Ти — Senior QA Automation Engineer. Твоє завдання — провести суворий аудит тексту.

ПРАВИЛА ПЕРЕВІРКИ:
1. ПОСИМВОЛЬНА ПЕРЕВІРКА (EN): Порівняй англійський текст у {% when "en" %} з прикладом у ТЗ. Будь-яка помилка в літерах (наприклад "Bok" замість "Book") — це ❌.
2. СТИЛЬ ТА СУТЬ: Якщо в ТЗ написано, що це "Гра тижня", а в тексті про це ні слова — це ❌.
3. ДОВЖИНА (UI Guard): Перевір довжину банерів (Header/Main). Якщо текст довший за 80-100 символів — став ⚠️ і вкажи кількість символів.
4. ЛОКАЛІЗАЦІЯ: Перевір зміст перекладів (DE, ES, FR тощо) на адекватність.

ФОРМАТ ВІДПОВІДІ:
============================================================
ОЦІНКА: [✅ / ❌ / ⚠️]
============================================================

📋 ЧЕК-ЛИСТ ЕЛЕМЕНТІВ:
- Subject: ✅
- Preheader: ✅
- Header Banner: ✅
- Main text banner: ✅
- Button Banner: ✅
- Header Main Text: ✅
- Main Text: ✅
- Button: ✅

📍 ДЕТАЛІЗАЦІЯ ПРОБЛЕМ:
(Якщо все ок — 'Проблем не виявлено'. Якщо є — чітко вкажи блок і суть)

💰 ПЕРЕВІРКА ВАЛЮТ:
(Тільки якщо знайдено суми текстом замість сніпетів)

1. 📝 ТЕХНІЧНИЙ АНАЛІЗ (Liquid & Length):
2. 🖋️ СЕМАНТИКА ТА ПЕРЕКЛАД:
============================================================"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"TECHNICAL REQUIREMENTS (TR):\n{tz_text}\n\nCOPYWRITER'S TEXT:\n{copy_text}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

def main():
    print("=" * 60)
    print(f"🚀 RP QA VALIDATOR v19.0 | Active Model: {MODEL_NAME}")
    print("=" * 60)

    # Step 1
    input("\n📋 Крок 1: Скопіюй ТЗ з ClickUp і натисни Enter...")
    raw_tz = pyperclip.paste().strip()
    tz_cleaned = clean_content(raw_tz)
    print("✅ ТЗ отримано та очищено.")

    # Step 2
    input("📲 Крок 2: Скопіюй текст Копірайтера і натисни Enter...")
    raw_copy = pyperclip.paste().strip()
    copy_cleaned = clean_content(raw_copy)
    print("✅ Текст отримано.")

    print("\n🤖 Аналіз за допомогою ШІ...")
    result = ai_validator(tz_cleaned, copy_cleaned)
    
    # Result
    print("\n" + result)
    pyperclip.copy(result)
    print("\n[✅ ЗВІТ СКОПІЙОВАНО В БУФЕР ОБМІНУ]")

if __name__ == "__main__":
    main()