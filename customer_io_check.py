import pyperclip
import re

def auto_discovery_checker_v6():
    print("📋 КРОК 1: Скопіюй таблицю з ClickUp")
    input("Натисни Enter...")
    clickup_data = pyperclip.paste()

    print("\n📲 КРОК 2: Скопіюй HTML-код з Customer.io")
    input("Натисни Enter...")
    cio_html = pyperclip.paste()

    def clean_text(text):
        if not text: return ""
        return " ".join(text.replace('&nbsp;', ' ').replace('\xa0', ' ').split())

    cio_clean = clean_text(cio_html)

    # Парсинг секцій
    lines = clickup_data.strip().split('\n')
    sections = []
    current_element = None
    
    for line in lines:
        line = line.strip()
        if not line or line in ["ELEMENT", "CONTENT"]: continue
        if not line.startswith('{%') and len(line) < 40:
            current_element = line
        elif current_element:
            sections.append((current_element, line))
            current_element = None

    # ВИТЯГУЄМО ЕТАЛОННИЙ СПИСОК МОВ (з першого знайденого Liquid-блоку)
    reference_langs = []
    for _, content in sections:
        found_langs = re.findall(r'{% when "([a-z]{2})" %}', content)
        if found_langs:
            reference_langs = sorted(found_langs)
            break

    print(f"\n{'='*60}\n🎯 СУВОРИЙ ЗВІТ (Еталон: {', '.join(reference_langs).upper()})\n{'='*60}")

    for name, content in sections:
        name_low = name.upper()
        print(f"\n🔍 {name_low}:")
        
        # Витягуємо мови з поточного блоку
        current_langs = re.findall(r'{% when "([a-z]{2})" %}', content)
        sorted_current = sorted(current_langs)

        # 1. ПЕРЕВІРКА СКЛАДУ МОВ (для всіх Liquid блоків)
        if current_langs:
            if sorted_current != reference_langs:
                missing = set(reference_langs) - set(sorted_current)
                extra = set(sorted_current) - set(reference_langs)
                print(f"   ❌ ПОМИЛКА МОВНОГО СКЛАДУ!")
                if missing: print(f"      - Відсутні мови: {list(missing)}")
                if extra:   print(f"      - Зайві/невірні мови: {list(extra)}")
            else:
                print(f"   ✅ Склад мов ідентичний еталону.")

        # 2. ПЕРЕВІРКА КОНТЕНТУ
        if "SUBJECT" in name_low or "PREHE" in name_low:
            # Для сабджектів перевіряємо лише наявність в ClickUp (вже перевірено вище)
            print(f"   ℹ️  Дані в ClickUp валідні.")
        else:
            # Для HTML блоків перевіряємо фізичну наявність в коді CIO
            clean_content = clean_text(content)
            if clean_content in cio_clean:
                print(f"   ✅ СТАТУС: Повний збіг у HTML!")
            else:
                if "{% when" in content:
                    print(f"   ⚠️ СТАТУС: Помилка в HTML! Деталі по мовах:")
                    languages = re.findall(r'({% when "([a-z]{2})" %}.*?)(?={% when|{% else|{% endcase)', content)
                    for full_match, lang_code in languages:
                        if clean_text(full_match) in cio_clean:
                            print(f"      [{lang_code.upper()}]: ✅ OK")
                        else:
                            print(f"      [{lang_code.upper()}]: ❌ НЕ ЗНАЙДЕНО В HTML")
                else:
                    # Для статичного тексту (наприклад, промокод)
                    if clean_content in cio_clean:
                        print(f"   ✅ СТАТУС: Знайдено в HTML!")
                    else:
                        print(f"   ❌ СТАТУС: Не знайдено в HTML!")

auto_discovery_checker_v6()