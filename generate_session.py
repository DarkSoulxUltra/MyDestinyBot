import os
import asyncio
try:
    from telethon.sync import TelegramClient
    from telethon.sessions import StringSession
except ImportError:
    print("Please install telethon first: pip install telethon")
    exit(1)

print("--- Telethon Session Generator ---")
print("You need your API_ID and API_HASH from https://my.telegram.org\n")

api_id = input("Enter your API_ID: ")
api_hash = input("Enter your API_HASH: ")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n--- YOUR STRING SESSION ---")
    print(client.session.save())
    print("---------------------------\n")
    print("Save this string securely! Anyone with this string can use your Telegram account.")
