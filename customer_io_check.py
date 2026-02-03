import pyperclip
import re

def auto_discovery_checker_v2():
    # 1. Завантажуємо дані
    print("📋 КРОК 1: Скопіюй таблицю з ClickUp")
    input("Натисни Enter...")
    clickup_data = pyperclip.paste()

    print("\n📲 КРОК 2: Скопіюй HTML-код з Customer.io")
    input("Натисни Enter...")
    cio_html = pyperclip.paste()

    print(f"\n{'='*60}\n🎯 АВТОМАТИЧНИЙ ЗВІТ (ЗНАЙДЕНО В CLICKUP)\n{'='*60}")
    
    # Очищуємо HTML для порівняння
    cio_clean = " ".join(cio_html.split())

    # Покращений пошук: 
    # ([^\n|]+) - шукаємо назву (будь-які символи, крім переносу або роздільника таблиці)
    # \s* - будь-яка кількість пробілів/табуляцій
    # (\{% case customer\.language %\}.*?\{% endcase %\}) - сам блок Liquid
    find_sections_pattern = r"([A-Z][A-Za-z\s]+)[\s|]+(\{% case customer\.language %\}.*?\{% endcase %\})"
    
    all_found = re.findall(find_sections_pattern, clickup_data, re.DOTALL)

    if not all_found:
        print("❌ Не вдалося розпізнати структуру таблиці.")
        print("💡 Порада: Переконайся, що при копіюванні захоплено і назву (напр. Button), і сам код.")
        return

    seen_content = set()

    for section_name, liquid_block in all_found:
        # Чистимо назву від зайвих пробілів та залишків таблиці
        clean_name = section_name.strip().split('\n')[-1].strip()
        
        # Унікальність за контентом
        content_hash = hash(liquid_block)
        if content_hash in seen_content:
            continue
            
        expected_liquid = " ".join(liquid_block.split())
        
        print(f"🔍 ПЕРЕВІРКА: {clean_name}")
        
        if expected_liquid in cio_clean:
            print(f"   ✅ СТАТУС: Ідеально співпадає!")
        else:
            print(f"   ❌ СТАТУС: ПОМИЛКА! Не знайдено в CIO.")
            # Виведемо шматочок того, що шукаємо, для візуальної перевірки
            print(f"      Шукав: {expected_liquid[:60]}...")
        
        seen_content.add(content_hash)

auto_discovery_checker_v2()