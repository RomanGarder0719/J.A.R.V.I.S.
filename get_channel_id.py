from telethon.sync import TelegramClient

api_id = 20250726        # ← сюда вставь свой API ID
api_hash = '52eae8f7a5484dce64aacb65a820d92e' # ← сюда вставь свой API Hash

phone = input("📱 Введи номер телефона (например, +79991234567): ")

with TelegramClient('user_session', api_id, api_hash) as client:
    client.send_code_request(phone)
    code = input("📩 Введи код, полученный по СМС или в Telegram: ")
    client.sign_in(phone, code)

    print("\n✅ Авторизация прошла успешно. Вот список чатов:\n")
    for dialog in client.iter_dialogs():
        print(f"{dialog.name} — {dialog.id}")
