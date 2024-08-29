import os
from dotenv import load_dotenv

load_dotenv()  # Это загружает файл .env

TOKEN = os.getenv('TOKEN')
LAWYER_CHAT_ID = os.getenv('LAWYER_CHAT_ID')
TOPIC_ID = os.getenv('TOPIC_ID')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')

# Добавьте это для отладки, чтобы убедиться, что переменные загружаются правильно
print(f"TOKEN={TOKEN}")
print(f"LAWYER_CHAT_ID={LAWYER_CHAT_ID}")
print(f"TOPIC_ID={TOPIC_ID}")
print(f"TARGET_CHAT_ID={TARGET_CHAT_ID}")
