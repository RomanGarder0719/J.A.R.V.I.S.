from dotenv import load_dotenv
import os

# Find .env file with os variables

# Конфигурация
VA_NAME = 'Jarvis'
VA_VER = "1.0"
VA_ALIAS = ("Джарвис", ";жарвис", "арвис", "арвес", "джава","чавес")
VA_TBR = ('скажи', 'покажи', 'ответь', 'произнеси', 'расскажи', 'сколько', 'слушай')

# ID микрофона (можете просто менять ID пока при запуске не отобразится нужный)
# -1 это стандартное записывающее устройство
MICROPHONE_INDEX = -1

# Путь к браузеру Google Chrome
CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe %s'

# Токен Picovoice
PICOVOICE_TOKEN = os.getenv('PICOVOICE_TOKEN')

# Токен OpenAI
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
