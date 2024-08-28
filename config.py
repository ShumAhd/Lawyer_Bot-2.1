import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
LAWYER_CHAT_ID = os.getenv('LAWYER_CHAT_ID')
TOPIC_ID = os.getenv('TOPIC_ID')
TARGET_CHAT_ID = os.getenv('TARGET_CHAT_ID')
