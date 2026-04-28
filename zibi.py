import telebot
import json
import os
import random
import io
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from rembg import remove
from PIL import Image

# --- CONFIGURARE ---
TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 
FISIER_MEMORIE = "zibi_memorie.json"
apiKey = "" # Rezervat pentru procesare AI daca este disponibila

bot = telebot.TeleBot(TOKEN, threaded=False)

class ZibiBrain:
    def __init__(self):
        self.default_mem = {
            "salut": ["Salut! Sunt Zibi, asistentul tău de încredere. 🌟"],
            "cine te-a creat": ["Creatorul meu este Brut Studio! 🚀"]
        }
        self.memorie = self.default_mem.copy()
        self.incarca()

    def incarca(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    if "date_memorie" in date:
                        self.memorie.update(date["date_memorie"])
            except: pass

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie}, f, ensure_ascii=False, indent=4)
        except: pass

zibi = ZibiBrain()

def extrage_informatie_wikipedia(query):
    """Cauta pe Wikipedia si extrage primul paragraf relevant."""
    try:
        # Pasul 1: Gasim link-ul de Wikipedia folosind DuckDuckGo (foarte rapid)
        search_query = f"{query} wikipedia romana"
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, region='wt-wt', max_results=3))
            
            url_wikipedia = None
            for r in results:
                if "wikipedia.org" in r['href']:
                    url_wikipedia = r['href']
                    break
            
            if not url_wikipedia and results:
                url_wikipedia = results[0]['href'] # Daca nu e wiki, luam prima sursa sigura

            if url_wikipedia:
                # Pasul 2: Descarcam pagina si extragem textul
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url_wikipedia, headers=headers, timeout=5)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Curatam codul inutil
                for s in soup(['script', 'style', 'table', 'aside']):
                    s.decompose()

                # Cautam paragrafele de text (Wikipedia are textul principal in <p>)
                paragrafe = soup.find_all('p')
                text_final = ""
                count = 0
                for p in paragrafe:
                    txt = p.get_text().strip()
                    if len(txt) > 50: # Ignoram fragmentele prea scurte
                        text_final += txt + "\n\n"
                        count += 1
                    if count >= 2: # Luam primele 2 paragrafe pentru un raspuns clar
                        break
                
                if text_final:
                    return f"📖 *Informație găsită:*\n\n{text_final}\n📍 _Sursa: {url_wikipedia}_"
    except Exception as e:
        print(f"Eroare extragere: {e}")
    return None

@bot.message_handler(content_types=['text', 'photo'])
def handle_messages(message):
    uid = message.from_user.id
    este_stapan = (uid == ID_STAPAN)
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # 1. INVATARE (Doar Stăpân, cu /)
    if este_stapan and text_mic.startswith("/invata"):
        partea = text_raw[len("/invata"):].strip()
        if ":" in partea:
            q, r = [x.strip() for x in partea.split(":", 1)]
            zibi.memorie[q.lower()] = [r]
            zibi.salveaza()
            bot.reply_to(message, f"✅ Memorat cu succes!")
        return

    # 2. IMAGINI (Rembg)
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Prelucrez imaginea, te rog așteaptă...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        try:
            output = remove(data)
            bot.send_document(message.chat.id, io.BytesIO(output), visible_file_name="zibi_fara_fundal.png")
        except: pass
        return

    # 3. LOGICA DE RASPUNS
    # Cautam intai in memoria locala (JSON)
    if text_mic in zibi.memorie:
        bot.reply_to(message, random.choice(zibi.memorie[text_mic]))
    else:
        # Daca nu e in memorie, Zibi cauta pe Wikipedia
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Curatam comanda "cauta" daca exista
        query = text_raw.lower().replace("cauta", "").replace("caută", "").strip()
        if not query: query = text_raw
        
        informatie = extrage_informatie_wikipedia(query)
        
        if informatie:
            bot.reply_to(message, informatie, parse_mode="Markdown")
        else:
            # Daca e stapanul, ii dam optiunea de invatare
            if este_stapan:
                bot.reply_to(message, "❌ Nu am găsit informația pe Wikipedia. Învață-mă: `/invata întrebare : răspuns`", parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Zibi - Expertul Wikipedia este Online!")
    bot.polling(none_stop=True)
