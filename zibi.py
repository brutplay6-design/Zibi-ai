import telebot
import json
import os
import random
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
                        # Curățăm spațiile invizibile
                        self.memorie = {k.strip().lower(): v for k, v in date["date_memorie"].items()}
                    self.tokens = date.get("tokens", 0)
            except: pass

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # --- PUSH PE GITHUB ---
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi a invatat lucruri noi! 🧠"])
                subprocess.run(["git", "push", "origin", "main"])
        except: pass

zibi = ZibiBrain()

# --- FUNCȚII LOGICĂ ---
def genereaza_epoca():
    toate = []
    for l in zibi.memorie.values(): toate.extend(l)
    if not toate: return "Memoria e goală..."
    cuvinte = " ".join(toate).split()
    if len(cuvinte) < 5: return random.choice(toate)
    res = " ".join(random.sample(cuvinte, min(7, len(cuvinte))))
    return f"🌀 [Epocă]: {res.capitalize()}..."

def alege_unic(lista):
    disp = [o for o in lista if o not in istoric_raspunsuri]
    ales = random.choice(disp if disp else lista)
    istoric_raspunsuri.append(ales)
    return ales

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    if text_mic == "/epoca": return genereaza_epoca()

    if uid == ID_STAPAN:
        if text_mic == "/reset_total":
            zibi.memorie = zibi.default_mem.copy()
            zibi.tokens = 0
            zibi.salveaza()
            return "💥 MEMORIE RESETATĂ!"

        if text_mic.startswith("/sterge"):
            c = text_mic.replace("/sterge", "").strip()
            if c in zibi.memorie:
                del zibi.memorie[c]
                zibi.salveaza()
                return f"🗑️ Sters: {c}"

        # --- INVATARE REPARATĂ (Ignoră cuvintele extra ca 'adult') ---
        if "/invata" in text_mic:
            linii = text_raw.split('\n')
            ok = 0
            for linie in linii:
                if ":" in linie:
                    try:
                        # Taiem tot ce e inainte de prima intrebare, ignorand 'adult' etc.
                        partea_de_dupa_invata = linie.split("/invata", 1)[1]
                        # Gasim unde e ":"
                        q_raw, r_raw = partea_de_dupa_invata.split(":", 1)
                        
                        # Curatam intrebarea (scoatem 'adult' daca a ramas in fata intrebarii)
                        q = q_raw.strip().lower()
                        if " " in q: # Daca a scris "/invata adult salut" -> q devine "adult salut"
                             q = q.split()[-1] # Luam doar ultimul cuvant: "salut"
                        
                        r = r_raw.strip()
                        
                        if q not in zibi.memorie: zibi.memorie[q] = []
                        if r not in zibi.memorie[q]:
                            zibi.memorie[q].append(r)
                            zibi.tokens += 10
                            ok += 1
                    except: continue
            if ok > 0:
                zibi.salveaza()
                return f"🚀 Succes! Am memorat {ok} amintiri noi! (Tokens: {zibi.tokens})"

    # --- RĂSPUNS ---
    if text_mic in zibi.memorie:
        return alege_unic(zibi.memorie[text_mic])

    chei = list(zibi.memorie.keys())
    m = get_close_matches(text_mic, chei, n=1, cutoff=0.3)
    if m: return alege_unic(zibi.memorie[m[0]])
    
    return "🤔 Nu știu asta. Învață-mă: /invata salut : Bună!"

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    bot.reply_to(message, proceseaza_mesaj(message.text, message.from_user.id))

if __name__ == "__main__":
    bot.polling(none_stop=True)
