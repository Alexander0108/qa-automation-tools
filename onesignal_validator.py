import pyperclip
import json
import re

def search_validator():
    try:
        print("\n📋 КРОК 1: Копіюй текст із таблиці Google (увесь блок)")
        input("Натисни Enter...")
        excel_dump = pyperclip.paste()

        print("\n📲 КРОК 2: Скопіюй Response з OneSignal")
        input("Натисни Enter...")
        os_payload = json.loads(pyperclip.paste()).get("payload", {})

        langs = ['en', 'tr', 'ru', 'uk', 'pl', 'de', 'es', 'fr', 'it', 'pt', 'ja', 'ko', 'nl', 'sv', 'fi', 'nb', 'da', 'no']

        print(f"\n{'='*70}\n📊 ЗВІТ ПЕРЕВІРКИ\n{'='*70}")

        url_match = re.search(r'https?://[^\s\t\n,"]+', excel_dump)
        expected_url = url_match.group(0).strip() if url_match else "ЛІНК НЕ ЗНАЙДЕНО"
        actual_url = str(os_payload.get('url', '')).strip()
        
        print(f"LINK: {'✅ OK' if actual_url == expected_url else '❌ ПОМИЛКА'}")
        if actual_url != expected_url:
            print(f"   [Excel]: {expected_url}\n   [OneSignal]: {actual_url}")

        os_headings = os_payload.get("headings", {})
        os_contents = os_payload.get("contents", {})

        for l in langs:
            title = os_headings.get(l)
            body = os_contents.get(l)

            if not title and not body:
                continue

            print(f"\n🌍 МОВА: {l.upper()}")

            t_search = str(title).strip()
            b_search = str(body).strip()

            t_found = t_search in excel_dump
            b_found = b_search in excel_dump

            if t_found:
                print(f"  ✅ Title: Знайдено")
            else:
                print(f"  ❌ Title: НЕ ЗНАЙДЕНО")
                print(f"     [OneSignal]:    '{t_search}'")
                # Просто підказка, щоб ти глянув у консоль вище, де весь текст таблиці
                print(f"     💡 Перевір пробіли або символи в Google Sheets!")

            if b_found:
                print(f"  ✅ Body:  Знайдено")
            else:
                print(f"  ❌ Body:  НЕ ЗНАЙДЕНО")
                print(f"     [OneSignal]:    '{b_search}'")
                print(f"     💡 Перевір пробіли або символи в Google Sheets!")

    except Exception as e:
        print(f"🚨 Помилка: {e}")

search_validator()