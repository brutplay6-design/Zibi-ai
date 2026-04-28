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
            "ce faci": ["Mă antrenez să fiu deștept! 🤖", "Stau pe GitHub și învăț. 💻"],
            "gluma": ["De ce are rinocerul corn? Ca să nu fie hipopotam supărat! 🦏"]
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
                        self.memorie = {k.strip().lower(): v for k, v in date["date_memorie"].items()}
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
                subprocess.run(["git", "commit", "-m", "Zibi a invatat sa combine mesaje! 🧠"])
                subprocess.run(["git", "push", "origin", "main"])
        except: pass

zibi = ZibiBrain()

def alege_unic(lista):
    disp = [o for o in lista if o not in istoric_raspunsuri]
    ales = random.choice(disp if disp else lista)
    istoric_raspunsuri.append(ales)
    return ales

# --- NOUA LOGICĂ DE COMBINARE A MESAJELOR ---
def genereaza_raspuns_complex(text_user):
    text_mic = text_user.lower().strip()
    raspunsuri_finale = []
    
    # 1. Căutăm potriviri pentru propoziții întregi sau bucăți de text
    # Verificăm dacă părți din memoria noastră se află în ce a scris userul
    for cheie in zibi.memorie.keys():
        if cheie in text_mic:
            raspunsuri_finale.append(alege_unic(zibi.memorie[cheie]))
    
    # 2. Dacă nu am găsit nimic prin căutare directă, încercăm get_close_matches pentru propoziția întreagă
    if not raspunsuri_finale:
        chei = list(zibi.memorie.keys())
        match = get_close_matches(text_mic, chei, n=1, cutoff=0.4)
        if match:
            raspunsuri_finale.append(alege_unic(zibi.memorie[match[0]]))

    # 3. Dacă tot nu avem nimic
    if not raspunsuri_finale:
        return "🤔 Interesant ce zici. Învață-mă: /invata intrebare : raspuns"

    # Unim toate răspunsurile găsite într-un singur mesaj
    return "\n".join(list(dict.fromkeys(raspunsuri_finale))) # dict.fromkeys scoate duplicatele

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    if text_mic == "/epoca":
        toate = []
        for l in zibi.memorie.values(): toate.extend(l)
        if not toate: return "Memorie goală."
        cuvinte = " ".join(toate).split()
        res = " ".join(random.sample(cuvinte, min(6, len(cuvinte))))
        return f"🌀 [Epocă]: {res.capitalize()}..."

    if uid == ID_STAPAN:
        if text_mic == "/reset_total":
            zibi.memorie = zibi.default_mem.copy()
            zibi.tokens = 0
            zibi.salveaza()
            return "💥 RESET TOTAL!"

        if text_mic.startswith("/invata"):
            linii = text_raw.split('\n')
            ok = 0
            for linie in linii:
                if ":" in linie:
                    try:
                        partea = linie.split("/invata", 1)[-1]
                        q, r = [x.strip() for x in partea.split(":", 1)]
                        q = q.lower()
                        if q not in zibi.memorie: zibi.memorie[q] = []
                        if r not in zibi.memorie[q]:
                            zibi.memorie[q].append(r)
                            zibi.tokens += 10
                            ok += 1
                    except: continue
            if ok > 0:
                zibi.salveaza()
                return f"🚀 Am învățat {ok} sensuri noi! (Tokens: {zibi.tokens})"

    return genereaza_raspuns_complex(text_raw)

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    bot.reply_to(message, proceseaza_mesaj(message.text, message.from_user.id))

if __name__ == "__main__":
    bot.polling(none_stop=True)
