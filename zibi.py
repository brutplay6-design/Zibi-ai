import telebot
import json
import os
import random
import io
import subprocess
from rembg import remove
from PIL import Image
import fitz  # PyMuPDF
from duckduckgo_search import DDGS
from collections import deque

# --- CONFIGURARE DATE ACCES ---
TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 

bot = telebot.TeleBot(TOKEN, threaded=False)
FISIER_MEMORIE = "zibi_memorie.json"

class ZibiBrain:
    def __init__(self):
        self.default_mem = {
            "salut": ["Salut! Sunt Zibi, asistentul tău creat de Brut Studio. 🌟"],
            "cine te-a creat": ["Creatorul meu este Brut Studio! 🚀"]
        }
        self.memorie = self.default_mem.copy()
        self.incarca_memorie()

    def incarca_memorie(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    if "date_memorie" in date:
                        self.memorie.update(date["date_memorie"])
            except: pass

    def salveaza_memorie(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie}, f, ensure_ascii=False, indent=4)
        except: pass

zibi = ZibiBrain()

def cauta_pe_internet(query):
    """Căutare inteligentă pe surse sigure."""
    try:
        # Curățăm interogația de prefixe
        text_pt_cautare = query.lower()
        prefixe = ["caută pe internet", "cauta pe internet", "caută pe interne", "caută", "cauta"]
        for p in prefixe:
            if text_pt_cautare.startswith(p):
                text_pt_cautare = text_pt_cautare[len(p):].strip()
                break
        
        if not text_pt_cautare:
            text_pt_cautare = query # Fallback la textul original dacă e prea scurt după tăiere

        with DDGS() as ddgs:
            # Adăugăm Wikipedia pentru a asigura surse sigure conform cerinței
            results = list(ddgs.text(f"{text_pt_cautare} wikipedia", region='wt-wt', max_results=3))
            if results:
                raspuns = f"🔎 *Informații găsite de Zibi pentru:* '{text_pt_cautare}'\n\n"
                for r in results:
                    raspuns += f"✅ *{r['title']}*\n{r['body'][:200]}...\n🔗 [Sursă]({r['href']})\n\n"
                return raspuns
    except Exception as e:
        print(f"Eroare search: {e}")
    return None

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_messages(message):
    uid = message.from_user.id
    este_stapan = (uid == ID_STAPAN)
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # --- 1. INVATARE: CU SLASH (Doar Stăpân) ---
    if este_stapan and text_mic.startswith("/invata"):
        try:
            partea = text_raw[len("/invata"):].strip()
            if ":" in partea:
                q, r = [x.strip() for x in partea.split(":", 1)]
                q_low = q.lower()
                if q_low not in zibi.memorie: zibi.memorie[q_low] = []
                zibi.memorie[q_low].append(r)
                zibi.salveaza_memorie()
                bot.reply_to(message, f"✅ Brut Studio, am memorat: {q}")
            else:
                bot.reply_to(message, "⚠️ Format corect: `/invata întrebare : răspuns`", parse_mode="Markdown")
        except: pass
        return

    # --- 2. CAUTARE: FĂRĂ SLASH (Detectare cuvânt cheie) ---
    if text_mic.startswith("caută") or text_mic.startswith("cauta"):
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat = cauta_pe_internet(text_raw)
        if rezultat:
            bot.reply_to(message, rezultat, parse_mode="Markdown")
        else:
            if este_stapan:
                bot.reply_to(message, "🤔 Nu am găsit nimic pe internet. Învață-mă: `/invata întrebare : răspuns`", parse_mode="Markdown")
        return

    # --- 3. PROCESARE IMAGINI (Rembg) ---
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Elimin fundalul...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        try:
            output = remove(data)
            bot.send_document(message.chat.id, io.BytesIO(output), visible_file_name="zibi_fara_fundal.png")
        except: pass
        return

    # --- 4. RĂSPUNS DIN MEMORIE SAU AUTO-SEARCH ---
    if text_mic in zibi.memorie:
        bot.reply_to(message, random.choice(zibi.memorie[text_mic]))
    else:
        # Dacă nu e în memorie, încearcă automat pe internet
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat_auto = cauta_pe_internet(text_raw)
        if rezultat_auto:
            bot.reply_to(message, rezultat_auto, parse_mode="Markdown")
        else:
            # Mesajul de "Nu știu" apare DOAR pentru tine (stăpânul)
            if este_stapan:
                bot.reply_to(message, "🤔 Nu am găsit informații în memorie sau pe net. Învață-mă: `/invata întrebare : răspuns`", parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Zibi Pro este ONLINE și configurat corect!")
    bot.polling(none_stop=True)
