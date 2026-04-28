import telebot
import json
import os
import random
import subprocess
import requests
from bs4 import BeautifulSoup
from collections import deque
from difflib import get_close_matches
import fitz  # PyMuPDF pentru PDF
from PIL import Image
import io

# --- CONFIGURARE ---
# Token-ul tau de la BotFather
TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 

bot = telebot.TeleBot(TOKEN, threaded=False)
FISIER_MEMORIE = "zibi_memorie.json"
istoric_raspunsuri = deque(maxlen=10)

class ZibiBrain:
    def __init__(self):
        self.default_mem = {
            "salut": ["Salut! Sunt Zibi, asistentul tau creat de Brut Studio si gazduit pe GitHub! 🌟"],
            "cine te-a creat": ["Creatorul meu este Brut Studio! 🚀"],
            "ce faci": ["Sunt online si procesez datele local, fara creier extern! 🤖"]
        }
        self.memorie = self.default_mem.copy()
        self.tokens = 0
        self.incarca()

    def incarca(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    if "date_memorie" in date:
                        self.memorie.update(date["date_memorie"])
                        self.tokens = date.get("tokens", 0)
            except: pass

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # Script pentru auto-commit pe GitHub daca ruleaza in Actions
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-Bot"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi si-a actualizat amintirile 🧠"])
                subprocess.run(["git", "push"])
        except: pass

zibi = ZibiBrain()

# --- FUNCTII PROCESARE (FARA API EXTERN) ---

def extrage_text_pdf(data_bytes):
    try:
        doc = fitz.open(stream=data_bytes, filetype="pdf")
        text = ""
        for pagina in doc:
            text += pagina.get_text()
        return text if text.strip() else "PDF-ul este gol sau are doar imagini."
    except Exception as e:
        return f"Eroare PDF: {str(e)}"

def cautare_web_simpla(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://www.google.com/search?q={query}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        rezultate = []
        for g in soup.find_all('h3'):
            rezultate.append(g.get_text())
        
        if rezultate:
            return "Am gasit pe internet:\n" + "\n".join([f"- {r}" for r in rezultate[:3]])
        return "Nu am gasit nimic nou pe web."
    except:
        return "Cercetarea web a esuat."

# --- LOGICA MESAJE ---

def proceseaza(message):
    uid = message.from_user.id
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # Gestionare Documente (PDF)
    if message.content_type == 'document' and message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        file_data = bot.download_file(file_info.file_path)
        continut = extrage_text_pdf(file_data)
        return f"📄 Rezumat PDF:\n\n{continut[:800]}..."

    # Gestionare Poze (Simpla notificare fara OCR extern greu)
    if message.content_type == 'photo':
        return "🖼️ Am primit poza! Momentan o pot stoca, dar am nevoie de un motor OCR extern pentru a citi textul din ea fara API."

    # Comanda Invatare (Stapan)
    if uid == ID_STAPAN and text_mic.startswith("/invata"):
        try:
            partea = text_raw.split("/invata", 1)[-1]
            q, r = [x.strip() for x in partea.split(":", 1)]
            q = q.lower()
            if q not in zibi.memorie: zibi.memorie[q] = []
            zibi.memorie[q].append(r)
            zibi.salveaza()
            return "✅ Am memorat in baza de date GitHub!"
        except: return "Format: /invata intrebare : raspuns"

    # Cautare Memorie sau Web
    if text_mic in zibi.memorie:
        return random.choice(zibi.memorie[text_mic])
    
    # Daca nu stie, cauta pe Google (Scraping)
    return cautare_web_simpla(text_raw)

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle(message):
    raspuns = proceseaza(message)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    print("Zibi este pornit...")
    bot.polling(none_stop=True)
