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

def cauta_pe_internet(query, este_stapan):
    """Funcție de căutare stabilă pe surse sigure."""
    try:
        search_query = query.lower()
        pentru_stergere = ["caută pe internet", "cauta pe internet", "caută", "cauta"]
        for cuvant in pentru_stergere:
            search_query = search_query.replace(cuvant, "")
        
        search_query = search_query.strip()
        if not search_query: 
            return "Ce anume vrei să caut?" if este_stapan else None

        with DDGS() as ddgs:
            results = list(ddgs.text(f"{search_query} wikipedia", region='wt-wt', max_results=3))
            if results:
                raspuns = f"🌐 *Informații găsite:* \n\n"
                for r in results:
                    raspuns += f"✅ *{r['title']}*\n{r['body'][:200]}...\n🔗 [Sursă]({r['href']})\n\n"
                return raspuns
    except Exception as e:
        print(f"Eroare search: {e}")
    
    # Mesajul de eroare apare DOAR pentru stăpân
    if este_stapan:
        return "🤔 Nu am găsit nimic clar pe internet. Poți să mă înveți folosind /invata"
    return None

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_messages(message):
    uid = message.from_user.id
    este_stapan = (uid == ID_STAPAN)
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # --- 1. INVATARE: CU SLASH (doar stăpân) ---
    if este_stapan and text_mic.startswith("/invata"):
        try:
            partea = text_raw[len("/invata"):].strip()
            if ":" in partea:
                q, r = [x.strip() for x in partea.split(":", 1)]
                q_low = q.lower()
                if q_low not in zibi.memorie: zibi.memorie[q_low] = []
                zibi.memorie[q_low].append(r)
                zibi.salveaza_memorie()
                bot.reply_to(message, f"✅ Memorat: {q}")
            else:
                bot.reply_to(message, "⚠️ Format: /invata întrebare : răspuns")
        except: pass
        return

    # --- 2. CAUTARE EXPLICITĂ: FĂRĂ SLASH ---
    if text_mic.startswith("caută") or text_mic.startswith("cauta"):
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat = cauta_pe_internet(text_raw, este_stapan)
        if rezultat:
            bot.reply_to(message, rezultat, parse_mode="Markdown")
        return

    # --- 3. PROCESARE IMAGINI ---
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
        # Căutare automată silențioasă
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat_auto = cauta_pe_internet(text_raw, este_stapan)
        if rezultat_auto:
            bot.reply_to(message, rezultat_auto, parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Zibi Privacy Fix este online!")
    bot.polling(none_stop=True)e:
        # Alegem un raspuns la intamplare din lista
        ales = random.choice(zibi.memorie[text_mic])
        bot.reply_to(message, ales)
    else:
        # Daca nu stie, cauta pe DuckDuckGo
        bot.send_chat_action(message.chat.id, 'typing')
        rezultat_web = cauta_pe_internet(text_raw)
        bot.reply_to(message, rezultat_web, parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Zibi Pro Telegram este ONLINE!")
    bot.polling(none_stop=True)                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
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
