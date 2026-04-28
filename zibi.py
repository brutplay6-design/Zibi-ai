import telebot
import json
import os
import random
import io
from rembg import remove
from PIL import Image
import fitz  # PyMuPDF
from duckduckgo_search import DDGS

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

def executa_cautare_web(query):
    """Căutare pe internet cu filtrare pentru subiect."""
    try:
        # Curățăm textul de cuvinte de comandă
        q_clean = query.lower()
        for v in ["caută pe internet", "cauta pe internet", "caută", "cauta", "/cauta"]:
            q_clean = q_clean.replace(v, "")
        
        q_clean = q_clean.strip()
        if not q_clean: return None

        with DDGS() as ddgs:
            # Căutăm informația
            results = list(ddgs.text(f"{q_clean} wikipedia", region='wt-wt', max_results=2))
            if results:
                raspuns = f"🌐 *Zibi a găsit pe internet:* \n\n"
                for r in results:
                    raspuns += f"✅ *{r['title']}*\n{r['body'][:250]}...\n🔗 [Vezi Sursa]({r['href']})\n\n"
                return raspuns
    except: pass
    return None

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_messages(message):
    uid = message.from_user.id
    este_stapan = (uid == ID_STAPAN)
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # 1. INVATARE (Doar Stăpân, obligatoriu cu /)
    if este_stapan and text_mic.startswith("/invata"):
        partea = text_raw[len("/invata"):].strip()
        if ":" in partea:
            q, r = [x.strip() for x in partea.split(":", 1)]
            q_low = q.lower()
            if q_low not in zibi.memorie: zibi.memorie[q_low] = []
            zibi.memorie[q_low].append(r)
            zibi.salveaza_memorie()
            bot.reply_to(message, f"✅ Am memorat lecția: {q}")
        else:
            bot.reply_to(message, "⚠️ Folosește formatul: `/invata întrebare : răspuns`", parse_mode="Markdown")
        return

    # 2. CAUTARE (Fără /)
    if text_mic.startswith("caută") or text_mic.startswith("cauta"):
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat = executa_cautare_web(text_raw)
        if rezultat:
            bot.reply_to(message, rezultat, parse_mode="Markdown")
        elif este_stapan:
            bot.reply_to(message, "🤔 Nu am găsit nimic pe net. Învață-mă tu!")
        return

    # 3. IMAGINI (Rembg)
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Elimin fundalul...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        try:
            output = remove(data)
            bot.send_document(message.chat.id, io.BytesIO(output), visible_file_name="zibi_fara_fundal.png")
        except: pass
        return

    # 4. LOGICĂ FINALĂ (Memorie -> Auto-Search -> Tăcere)
    if text_mic in zibi.memorie:
        bot.reply_to(message, random.choice(zibi.memorie[text_mic]))
    else:
        # Dacă nu știe din memorie, încearcă automat pe net
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat_auto = executa_cautare_web(text_raw)
        if rezultat_auto:
            bot.reply_to(message, rezultat_auto, parse_mode="Markdown")
        else:
            # Doar stăpânul vede eroarea dacă și netul eșuează
            if este_stapan:
                bot.reply_to(message, "🤔 Nu știu acest subiect. Învață-mă: `/invata întrebare : răspuns`", parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling(none_stop=True)
