import telebot
import json
import os
import random
import requests
import time

# --- CONFIGURARE ---
TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 
FISIER_NEURONI = "zibi_neuroni.json"

bot = telebot.TeleBot(TOKEN)

class CreierEvolutiv:
    def __init__(self):
        self.cale = FISIER_NEURONI
        self.model = self.incarca()
        # Alfabetul complet pe care Zibi il poate folosi
        self.caractere_permise = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?  🤖🌟🚀✅"

    def incarca(self):
        if os.path.exists(self.cale):
            try:
                with open(self.cale, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

    def salveaza(self):
        try:
            with open(self.cale, "w", encoding="utf-8") as f:
                json.dump(self.model, f, ensure_ascii=False, indent=2)
        except: pass

    def antreneaza_pe_text(self, text):
        """Invata combinatiile de caractere din textul primit."""
        ordin = 3
        if len(text) <= ordin: return
        
        for i in range(len(text) - ordin):
            gram = text[i:i+ordin]
            urmatorul = text[i+ordin]
            if gram not in self.model:
                self.model[gram] = {}
            if urmatorul not in self.model[gram]:
                self.model[gram][urmatorul] = 0
            self.model[gram][urmatorul] += 1

    def genereaza(self, inceput, lungime=60):
        """Construieste un raspuns litera cu litera."""
        if not self.model: return "🤖... (Neuroni goi. Folosește /epoca)"
        
        # Incepem cu ceva din memorie daca inceputul nu exista
        gram = inceput[:3] if inceput[:3] in self.model else random.choice(list(self.model.keys()))
        rezultat = gram

        for _ in range(lungime):
            if gram in self.model:
                optiuni = self.model[gram]
                urmatorul = random.choices(list(optiuni.keys()), weights=list(optiuni.values()))[0]
                rezultat += urmatorul
                gram = rezultat[-3:]
                if urmatorul in ".!?": break # Se opreste la final de propozitie
            else:
                break
        return rezultat

zibi_ai = CreierEvolutiv()

def preia_date_wiki():
    """Ofera materie prima pentru antrenament."""
    subiecte = ["Tehnologie", "Moldova", "Robot", "Univers", "Viitor", "Istorie", "Stiinta"]
    subiect = random.choice(subiecte)
    try:
        url = "https://ro.wikipedia.org/w/api.php"
        params = {"action": "query", "prop": "extracts", "exintro": True, "explaintext": True, "titles": subiect, "format": "json"}
        res = requests.get(url, params=params).json()
        pagini = res['query']['pages']
        for id in pagini:
            return pagini[id].get('extract', "")
    except: return None

@bot.message_handler(commands=['epoca'])
def comanda_epoca(message):
    if message.from_user.id != ID_STAPAN: return
    
    try:
        # Luam numarul de epoci din textul comenzii (ex: /epoca 5)
        parti = message.text.split()
        numar_epoci = int(parti[1]) if len(parti) > 1 else 1
        
        status_msg = bot.reply_to(message, f"🧬 Încep antrenamentul autonom pentru {numar_epoci} epoci...")
        
        for e in range(numar_epoci):
            bot.edit_message_text(f"🧠 Epoca {e+1}/{numar_epoci} în curs... Combin litere, cifre și emoji...", message.chat.id, status_msg.message_id)
            
            # Pasul de invatare: Zibi "citeste" si proceseaza date noi
            date_noi = preia_date_wiki()
            if date_noi:
                zibi_ai.antreneaza_pe_text(date_noi)
                time.sleep(1) # Pauza mica sa nu blocheze procesorul
        
        zibi_ai.salveaza()
        bot.edit_message_text(f"✅ Antrenament finalizat! Am acum {len(zibi_ai.model)} conexiuni neuronale.", message.chat.id, status_msg.message_id)
    except:
        bot.reply_to(message, "⚠️ Format: `/epoca [număr]` (ex: /epoca 5)", parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text
    # Zibi invata si din ce scrii tu (Feedback Loop)
    zibi_ai.antreneaza_pe_text(text)
    
    bot.send_chat_action(message.chat.id, 'typing')
    raspuns = zibi_ai.genereaza(text)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    print("🚀 Zibi este gata pentru antrenament pe epoci!")
    bot.polling(none_stop=True)            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie}, f, ensure_ascii=False, indent=4)
        except: pass

zibi = ZibiBrain()

def cauta_wikipedia_direct(query):
    """Foloseste API-ul oficial Wikipedia pentru a lua text direct."""
    try:
        # Curatam query-ul
        query = query.lower().replace("cauta", "").replace("caută", "").strip()
        
        # Seteaza limba romana
        S = requests.Session()
        URL = "https://ro.wikipedia.org/w/api.php"

        # Pasul 1: Cautam titlul paginii
        PARAMS_SEARCH = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }
        res_search = S.get(url=URL, params=PARAMS_SEARCH, timeout=5).json()
        
        if not res_search['query']['search']:
            return None

        titlu = res_search['query']['search'][0]['title']

        # Pasul 2: Luam extrasul (textul) paginii respective
        PARAMS_TEXT = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": titlu,
            "format": "json"
        }
        res_text = S.get(url=URL, params=PARAMS_TEXT, timeout=5).json()
        pages = res_text['query']['pages']
        
        for p in pages:
            extras = pages[p]['extract']
            if extras:
                # Scurtam daca e prea lung
                if len(extras) > 800:
                    extras = extras[:800] + "..."
                return f"📖 *Informație Wikipedia: {titlu}*\n\n{extras}"
                
    except Exception as e:
        print(f"Eroare API Wiki: {e}")
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
            bot.reply_to(message, "✅ Memorat!")
        return

    # 2. IMAGINI (Rembg)
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "🖼️ Elimin fundalul...")
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        try:
            output = remove(data)
            bot.send_document(message.chat.id, io.BytesIO(output), visible_file_name="zibi_no_bg.png")
        except: pass
        return

    # 3. LOGICA RASPUNS
    # A. Verifica in JSON
    if text_mic in zibi.memorie:
        bot.reply_to(message, random.choice(zibi.memorie[text_mic]))
        return

    # B. Daca nu e in memorie, cauta AUTOMAT pe Wikipedia (Direct API)
    bot.send_chat_action(message.chat.id, 'typing')
    raspuns_wiki = cauta_wikipedia_direct(text_raw)
    
    if raspuns_wiki:
        bot.reply_to(message, raspuns_wiki, parse_mode="Markdown")
    else:
        # Mesajul de eroare apare DOAR pentru tine
        if este_stapan:
            bot.reply_to(message, "❌ Nu am găsit nimic pe Wikipedia. Învață-mă: `/invata întrebare : răspuns`", parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling(none_stop=True)
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
