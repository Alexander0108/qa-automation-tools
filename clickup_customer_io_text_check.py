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
        
        system_msg = f"""Ти — Senior QA Engineer. Твоє завдання — аудит iGaming контенту. 
Будь розумним: розрізняй критичні помилки, що ламають логіку, та незначні стилістичні варіації.

ПРАВИЛА ПЕРЕВІРКИ:
1. КРИТИЧНО (❌): 
   - Неправильні сніпети (напр. {{{{snippets['20_EUR']}}}} замість 10_EUR).
   - Помилки в цифрах або промокодах (LOVE65 vs LOVE60).
   - Порушення HTML-структури (напр. не закритий тег <strong>, що ламає верстку).
   - Розбіжність даних між EN та іншими мовами (Source of Truth).

2. ДОПУСТИМО (✅ - ігноруй):
   - Варіації в лейблах термзів: "Min.dep:", "Min Deposit:", "Minimum Deposit:" — це все ОК, якщо сніпет поруч вірний.
   - Регістр у лейблах: "Promo code:" vs "Promo Code:" — це ОК.
   - Крапки в кінці міток (Max.win vs Max Win) — не вважати помилкою.

3. ПРЕХЕДЕР: Перевіряй тільки наявність сенсу "терміновості", не чіпляйся до слів.

ФОРМАТ ВІДПОВІДІ:
============================================================
ОЦІНКА: [✅ / ❌ / ⚠️]
============================================================
📋 ЧЕК-ЛИСТ:
- Суть та логіка: [Статус]
- Технічна цілісність (HTML/Сніпети): [Статус]
- Локалізація: [Статус]

📍 ДЕТАЛІЗАЦІЯ:
- Описуй ТІЛЬКИ те, що реально ламає логіку або суперечить ТЗ за цифрами/структурою. Не пиши про дрібні розбіжності в назвах полів.
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