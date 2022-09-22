import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
CHANNELS_FOR_SUB =[f"@{ch[13:]}" for ch in open('channels.txt', 'r', encoding='utf-8').read().split('\n')]
