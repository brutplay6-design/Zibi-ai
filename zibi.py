import telebot
import json
import os
import random
import threading
import subprocess
from collections import deque
from difflib import get_close_matches

# --- DATE ACCES ---
TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 

bot = telebot.TeleBot(TOKEN, threaded=False)
FISIER_MEMORIE = "zibi_memorie.json"
istoric_raspunsuri = deque(maxlen=10)

class ZibiBrain:
    def __init__(self):
        self.default_mem = {
            "salut": ["Salutare! 🌟", "Hei! 😎"],
            "gluma": ["Ce face o vacă pe lună? Muuu-nwalk! 🐄"]
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
                        for k, v in date["date_memorie"].items():
                            # Ne asigurăm că toate cheile sunt litere mici
                            self.memorie[k.lower().strip()] = v if isinstance(v, list) else [v]
                    self.tokens = date.get("tokens", 0)
            except: pass

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi si-a imbunatatit memoria! 🧠"])
                subprocess.run(["git", "push"])
        except: pass

zibi = ZibiBrain()

def genereaza_epoca():
    toate_raspunsurile = []
    for lista in zibi.memorie.values():
        toate_raspunsurile.extend(lista)
    if not toate_raspunsurile: return "Creierul meu e gol..."
    cuvinte_totale = " ".join(toate_raspunsurile).split()
    if len(cuvinte_totale) < 4: return random.choice(toate_raspunsurile)
    lungime = random.randint(4, 10)
    selectie = random.sample(cuvinte_totale, min(lungime, len(cuvinte_totale)))
    return "🌀 [Epocă]: " + " ".join(selectie).capitalize() + "..."

def alege_unic(lista_optiuni):
    disponibile = [opt for opt in lista_optiuni if opt not in istoric_raspunsuri]
    ales = random.choice(disponibile if disponibile else lista_optiuni)
    istoric_raspunsuri.append(ales)
    return ales

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    if text_mic == "/epoca":
        return genereaza_epoca()

    if uid == ID_STAPAN:
        if text_mic == "/reset_total":
            zibi.memorie = zibi.default_mem.copy()
            zibi.tokens = 0
            zibi.salveaza()
            return "💥 RESETARE COMPLETĂ!"

        if text_mic.startswith("/sterge"):
            cuv = text_mic.replace("/sterge", "").strip()
            if cuv in zibi.memorie:
                del zibi.memorie[cuv]
                zibi.salveaza()
                return f"🗑️ Am șters '{cuv}'."
            return "❓ Nu l-am găsit."

        if text_mic.startswith("/invata"):
            linii = text_raw.split('\n')
            inv = 0
            for linie in linii:
                l_curat = linie.replace("/invata", "").strip()
                if ":" in l_curat:
                    try:
                        q, r = [x.strip() for x in l_curat.split(":", 1)]
                        q = q.lower()
                        if q not in zibi.memorie: zibi.memorie[q] = []
                        if r not in zibi.memorie[q]:
                            zibi.memorie[q].append(r)
                            zibi.tokens += 10
                            inv += 1
                    except: continue
            if inv > 0:
                zibi.salveaza()
                return f"🚀 Învățat {inv} chestii noi! (Tokens: {zibi.tokens})"

    # --- LOGICA DE RĂSPUNS ÎMBUNĂTĂȚITĂ ---
    # Pasul 1: Căutare exactă
    if text_mic in zibi.memorie:
        return alege_unic(zibi.memorie[text_mic])

    # Pasul 2: Căutare aproximativă (mai relaxată acum)
    chei = list(zibi.memorie.keys())
    potrivire = get_close_matches(text_mic, chei, n=1, cutoff=0.3) # Cutoff redus de la 0.5 la 0.3
    
    if potrivire:
        return alege_unic(zibi.memorie[potrivire[0]])
    
    return "🤔 Nu știu asta. Învață-mă: /invata " + text_mic + " : răspunsul tău"

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    raspuns = proceseaza_mesaj(message.text, message.from_user.id)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    bot.polling(none_stop=True)
