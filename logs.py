import logging
from datetime import datetime
import os

# Cria a pasta de logs se não existir
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log", encoding='utf-8'),
        logging.StreamHandler() # Mostra no console também
    ]
)

def log_info(mensagem):
    logging.info(mensagem)

def log_erro(mensagem):
    logging.error(mensagem)