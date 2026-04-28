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

def cauta_surse_sigure(query):
    """Căutare pe internet folosind DuckDuckGo."""
    try:
        search_query = f"{query} wikipedia"
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, region='wt-wt', max_results=3))
            if results:
                raspuns = f"🔎 *Informații găsite pentru:* '{query}'\n\n"
                for r in results:
                    raspuns += f"✅ *{r['title']}*\n📝 {r['body'][:200]}...\n🔗 [Sursă]({r['href']})\n\n"
                return raspuns
    except: pass
    return "🤔 Nu am găsit detalii sigure pe internet pentru acest subiect."

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_messages(message):
    uid = message.from_user.id
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # --- INVATARE: CU SLASH (obligatoriu) ---
    # Exemplu: /invata cine e seful : Brut Studio
    if uid == ID_STAPAN and text_mic.startswith("/invata"):
        try:
            partea = text_raw[len("/invata"):].strip()
            if ":" in partea:
                q, r = [x.strip() for x in partea.split(":", 1)]
                q_low = q.lower()
                if q_low not in zibi.memorie: zibi.memorie[q_low] = []
                zibi.memorie[q_low].append(r)
                zibi.salveaza_memorie()
                bot.reply_to(message, f"✅ Am memorat: {q}")
                return
            else:
                bot.reply_to(message, "⚠️ Folosește formatul: /invata întrebare : răspuns")
                return
        except: pass

    # --- CAUTARE: FĂRĂ SLASH ---
    # Exemplu: cauta vremea in bucuresti
    if text_mic.startswith("cauta"):
        subiect = text_raw[len("cauta"):].strip()
        if subiect:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.reply_to(message, cauta_surse_sigure(subiect), parse_mode="Markdown")
            return

    # --- PROCESARE IMAGINI ---
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Elimin fundalul...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        try:
            output = remove(data)
            bot.send_document(message.chat.id, io.BytesIO(output), visible_file_name="zibi_fara_fundal.png")
        except: pass
        return

    # --- RĂSPUNS MEMORIE SAU AUTO-SEARCH ---
    if text_mic in zibi.memorie:
        bot.reply_to(message, random.choice(zibi.memorie[text_mic]))
    else:
        # Dacă nu știe, caută automat
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, cauta_surse_sigure(text_raw), parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Zibi Pro este online (/invata + cauta fara slash)")
    bot.polling(none_stop=True)                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date_incarcate = json.load(f)
                    if "date_memorie" in date_incarcate:
                        # Combinam memoria default cu cea salvata
                        for q, r_list in date_incarcate["date_memorie"].items():
                            q_clean = q.strip().lower()
                            if q_clean not in self.memorie:
                                self.memorie[q_clean] = r_list
                            else:
                                # Adaugam raspunsuri noi la intrebari existente fara duplicate
                                self.memorie[q_clean] = list(set(self.memorie[q_clean] + r_list))
                print("✅ Memoria a fost incarcata cu succes din fisier!")
            except Exception as e:
                print(f"⚠️ Eroare la incarcarea memoriei: {e}")

    def salveaza_memorie(self):
        """Salveaza tot ce a invatat Zibi inapoi in fisier."""
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie}, f, ensure_ascii=False, indent=4)
            
            # PUSH AUTOMAT PE GITHUB (Daca ruleaza in Github Actions)
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-AutoSave"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi si-a salvat amintirile noi! 🧠"])
                subprocess.run(["git", "push"])
        except Exception as e:
            print(f"⚠️ Eroare la salvarea memoriei: {e}")

zibi = ZibiBrain()

# --- FUNCTII DE PROCESARE (FARA API EXTERN) ---

def cauta_pe_internet(query):
    """Cauta informatii pe web folosind DuckDuckGo Search."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='wt-wt', max_results=3)
            if results:
                raspuns = "🌐 Am cautat pe internet si iata ce am gasit:\n\n"
                for r in results:
                    raspuns += f"🔹 *{r['title']}*\n{r['href']}\n\n"
                return raspuns
    except Exception as e:
        print(f"Eroare cautare: {e}")
    return "🤔 Nu am gasit nimic in memorie si cautarea web a intampinat o problema."

def scoate_fundal(data_bytes):
    """Elimina fundalul unei imagini folosind biblioteca rembg."""
    try:
        input_image = Image.open(io.BytesIO(data_bytes))
        output_image = remove(input_image)
        img_io = io.BytesIO()
        output_image.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io
    except Exception as e:
        print(f"Eroare rembg: {e}")
        return None

def citeste_pdf(data_bytes):
    """Extrage primele caractere dintr-un document PDF."""
    try:
        doc = fitz.open(stream=data_bytes, filetype="pdf")
        text = ""
        for pagina in doc:
            text += pagina.get_text()
        return text[:1500] if text.strip() else "Documentul PDF nu contine text citibil."
    except Exception as e:
        return f"Eroare la citirea PDF: {e}"

# --- LOGICA MESAJE TELEGRAM ---

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_messages(message):
    uid = message.from_user.id
    text_raw = message.text or message.caption or ""
    text_mic = text_raw.lower().strip()

    # 1. Gestionare PDF-uri
    if message.content_type == 'document' and message.document.mime_type == 'application/pdf':
        bot.send_chat_action(message.chat.id, 'typing')
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)
        rezultat = citeste_pdf(data)
        bot.reply_to(message, f"📄 *Continut PDF:*\n\n{rezultat}", parse_mode="Markdown")
        return

    # 2. Gestionare Poze (Eliminare fundal)
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Elimin fundalul pozei, te rog asteapta...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        img_fara_bg = scoate_fundal(data)
        if img_fara_bg:
            bot.send_document(message.chat.id, img_fara_bg, visible_file_name="zibi_fara_fundal.png")
        else:
            bot.reply_to(message, "❌ Nu am putut elimina fundalul.")
        return

    # 3. Functia de INVATARE (Doar pentru Stapan)
    if uid == ID_STAPAN and text_mic.startswith("/invata"):
        try:
            # Format dorit: /invata intrebare : raspuns
            partea = text_raw.split("/invata", 1)[-1]
            if ":" in partea:
                intrebare, raspuns = [x.strip() for x in partea.split(":", 1)]
                intrebare_mic = intrebare.lower()
                
                if intrebare_mic not in zibi.memorie:
                    zibi.memorie[intrebare_mic] = []
                
                if raspuns not in zibi.memorie[intrebare_mic]:
                    zibi.memorie[intrebare_mic].append(raspuns)
                    zibi.salveaza_memorie()
                    bot.reply_to(message, f"✅ Brut Studio, am invatat:\n❓ {intrebare}\n💡 {raspuns}")
                else:
                    bot.reply_to(message, "Asta stiu deja! 😉")
            else:
                bot.reply_to(message, "Te rog foloseste formatul -> /invata intrebare : raspuns")
        except Exception as e:
            bot.reply_to(message, f"Eroare la invatare: {e}")
        return

    # 4. Comanda Reset (Doar Stapan)
    if uid == ID_STAPAN and text_mic == "/reset_total":
        zibi.memorie = zibi.default_mem.copy()
        zibi.salveaza_memorie()
        bot.reply_to(message, "💥 Memoria a fost resetata la valorile din fabrica!")
        return

    # 5. Cautare in memorie sau pe Web
    if text_mic in zibi.memorie:
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
