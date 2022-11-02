import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
CHANNELS = json.loads(open('channels.json', 'r', encoding='utf-8').read())