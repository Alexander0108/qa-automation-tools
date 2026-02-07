import pyperclip
import re

HEADER_ELEMENT = "ELEMENT"
HEADER_CONTENT = "CONTENT"
MAX_ELEMENT_NAME_LEN = 40


def clean_text(text):
    if not text:
        return ""
    return " ".join(text.replace("&nbsp;", " ").replace("\xa0", " ").split())


def parse_clickup_sections(clickup_data: str) -> list[tuple[str, str]]:
    """Парсить таблицю ClickUp: пари (назва елемента, контент). Контент може бути багаторядковим."""
    lines = clickup_data.strip().split("\n")
    sections = []
    current_element = None
    current_content_lines = []

    def flush():
        nonlocal current_element, current_content_lines
        if current_element and current_content_lines:
            sections.append((current_element, "\n".join(current_content_lines)))
        current_content_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped in (HEADER_ELEMENT, HEADER_CONTENT):
            continue
        # Новий елемент: короткий рядок без Liquid
        if not stripped.startswith("{%") and len(stripped) < MAX_ELEMENT_NAME_LEN:
            flush()
            current_element = stripped
        elif current_element:
            current_content_lines.append(stripped)

    flush()
    return sections


def auto_discovery_checker_v6():
    print("📋 КРОК 1: Скопіюй таблицю з ClickUp")
    input("Натисни Enter...")
    clickup_data = pyperclip.paste().strip()
    if not clickup_data:
        print("❌ Буфер порожній. Скопіюй таблицю з ClickUp і запусти знову.")
        return

    print("\n📲 КРОК 2: Скопіюй HTML-код з Customer.io")
    input("Натисни Enter...")
    cio_html = pyperclip.paste().strip()
    if not cio_html:
        print("❌ Нічого не знайдено в буфері. Скопіюй HTML або результат grabber.")
        return

    cio_clean = clean_text(cio_html)

    sections = parse_clickup_sections(clickup_data)

    # Еталонний список мов з першого Liquid-блоку
    reference_langs = []
    for _, content in sections:
        found_langs = re.findall(r'{% when "([a-z]{2})" %}', content)
        if found_langs:
            reference_langs = sorted(found_langs)
            break

    ref_label = ", ".join(reference_langs).upper() if reference_langs else "(немає Liquid-блоків)"
    print(f"\n{'='*60}\n🎯 СУВОРИЙ ЗВІТ (Еталон мов: {ref_label})\n{'='*60}")

    ok_count = 0
    fail_count = 0
    liquid_block_re = re.compile(
        r'({% when "([a-z]{2})" %}.*?)(?={% when|{% else|{% endcase)',
        re.DOTALL,
    )

    for name, content in sections:
        name_low = name.upper()
        print(f"\n🔍 {name_low}:")

        current_langs = re.findall(r'{% when "([a-z]{2})" %}', content)
        sorted_current = sorted(current_langs)

        # 1. Перевірка складу мов (Liquid-блоки)
        if current_langs:
            if sorted_current != reference_langs:
                fail_count += 1
                missing = set(reference_langs) - set(sorted_current)
                extra = set(sorted_current) - set(reference_langs)
                print(f"   ❌ ПОМИЛКА МОВНОГО СКЛАДУ!")
                if missing:
                    print(f"      - Відсутні мови: {list(missing)}")
                if extra:
                    print(f"      - Зайві/невірні мови: {list(extra)}")
            else:
                print(f"   ✅ Склад мов ідентичний еталону.")

        # 2. Перевірка наявності контенту в HTML CIO
        if "SUBJECT" in name_low or "PREHE" in name_low:
            print(f"   ℹ️  Дані в ClickUp валідні.")
            ok_count += 1
        else:
            clean_content = clean_text(content)
            if clean_content in cio_clean:
                print(f"   ✅ СТАТУС: Повний збіг у HTML!")
                ok_count += 1
            else:
                if "{% when" in content:
                    print(f"   ⚠️ СТАТУС: Помилка в HTML! Деталі по мовах:")
                    lang_ok = 0
                    for full_match, lang_code in liquid_block_re.findall(content):
                        if clean_text(full_match) in cio_clean:
                            print(f"      [{lang_code.upper()}]: ✅ OK")
                            lang_ok += 1
                        else:
                            print(f"      [{lang_code.upper()}]: ❌ НЕ ЗНАЙДЕНО В HTML")
                    if lang_ok == len(current_langs):
                        ok_count += 1
                    else:
                        fail_count += 1
                else:
                    print(f"   ❌ СТАТУС: Не знайдено в HTML!")
                    fail_count += 1

    print(f"\n{'='*60}\n📊 Підсумок: ✅ {ok_count} | ❌ {fail_count}\n{'='*60}")


if __name__ == "__main__":
    auto_discovery_checker_v6()