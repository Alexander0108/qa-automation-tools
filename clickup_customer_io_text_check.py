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

# Вибір моделі з файлу .env. За замовчуванням використовується gpt-4o-mini
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ==========================================================
# CORE LOGIC
# ==========================================================

def clean_content(text: str) -> str:
    """Очищення тексту від технічного шуму CRM та ClickUp."""
    text = re.sub(r'https?://\S*(?:png|jpg|jpeg|gif|svg|webp)\S*', '', text)
    lines = text.split('\n')
    ignore_list = ['element', 'content', 'design', 'https']
    cleaned = [line.strip() for line in lines if line.strip() and not any(x in line.lower() for x in ignore_list)]
    return "\n".join(cleaned)

def ai_validator(tz_text: str, copy_text: str) -> str:
    """ШІ-двигун v20.5: Cross-language Localization & HTML Integrity."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "❌ ERROR: OPENAI_API_KEY not found in .env file!"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        system_msg = f"""Ти — Senior Localization QA Engineer в iGaming. Твоє завдання — аудит мультимовного контенту.

ПРАВИЛА ПЕРЕВІРКИ:
1. SOURCE OF TRUTH (EN): Англійський текст ({{% when "en" %}}) є еталоном. Всі інші локалізації (DE, ES, FR, IT тощо) МАЮТЬ точно відповідати йому за змістом, цифрами (бонуси, вейджери) та промокодами. 
   - Якщо в EN "65 FS", а в локалі інша цифра — це ❌.
   - Якщо в EN є промокод, а в локалі його немає — це ❌.

2. HTML-СТРУКТУРА: Перевір 'Приклад стилю' в ТЗ. Якщо в прикладі <strong>Wager:</strong> x40, а копірайтер написав <strong>Wager: x40</strong> — це ❌. Теги <span> мають бути лише там, де вказано в стилі.

3. ТЕРМЗИ (T&C): Перевір наявність валютних сніпетів (напр. {{{{snippets['10_EUR']}}}}). Вони мають бути однаковими у всіх мовах.

4. СТИСЛІСТЬ: Якщо розділ пройдено успішно (✅) — пиши лише одну коротку фразу. Деталізуй ТІЛЬКИ помилки.

ФОРМАТ ВІДПОВІДІ:
============================================================
ОЦІНКА: [✅ / ❌ / ⚠️]
============================================================
📋 ЧЕК-ЛИСТ:
- Subject/Preheader (vs EN): [Статус]
- Banners (vs EN): [Статус]
- Terms & Conditions (HTML & Data): [Статус]
- Localization Audit (Consistency): [Статус: чи всі мови відповідають EN-версії]

📍 ДЕТАЛІЗАЦІЯ ПОМИЛОК:
- (Якщо є помилки, вкажи конкретну мову та суть проблеми)
============================================================"""

        # Адаптація температури для нових моделей
        is_modern = any(m in MODEL_NAME for m in ["gpt-5", "o1-", "o3-"])
        current_temp = 1 if is_modern else 0

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"TECHNICAL REQUIREMENTS (TR):\n{tz_text}\n\nCOPYWRITER'S TEXT:\n{copy_text}"}
            ],
            temperature=current_temp
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

def main():
    print("=" * 60)
    print(f"🚀 RP QA VALIDATOR v20.5 | Active Model: {MODEL_NAME}")
    print("=" * 60)

    # Step 1: Technical Requirements
    input("\n📋 Крок 1: Скопіюй ТЗ з ClickUp і натисни Enter...")
    tz_cleaned = clean_content(pyperclip.paste().strip())
    print("✅ ТЗ отримано та очищено.")

    # Step 2: Copywriter Text
    input("📲 Крок 2: Скопіюй текст Копірайтера і натисни Enter...")
    copy_cleaned = clean_content(pyperclip.paste().strip())
    print("✅ Текст отримано.")

    print(f"\n🤖 Аналіз за допомогою {MODEL_NAME}...")
    result = ai_validator(tz_cleaned, copy_cleaned)
    
    # Формування звіту з технічним підписом
    temp_display = "1.0" if any(m in MODEL_NAME for m in ["gpt-5", "o1-", "o3-"]) else "0.0"
    final_report = result + f"\n\n⚙️ Validated by AI Engine: {MODEL_NAME} (Temp: {temp_display})"
    
    # Вивід результату та копіювання в буфер
    print("\n" + final_report)
    pyperclip.copy(final_report)
    print("\n[✅ ЗВІТ СКОПІЙОВАНО В БУФЕР ОБМІНУ]")

if __name__ == "__main__":
    main()