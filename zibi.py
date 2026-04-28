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
        # Setăm identitatea corectă direct în codul de bază
        self.default_mem = {
            "salut": ["Salut! Sunt asistentul Brut Studio. 🌟"],
            "cine te-a creat": ["Creatorul meu este Brut Studio! 🚀"],
            "creator": ["Brut Studio m-a adus la viață. 😎"],
            "ce faci": ["Sunt online și gata de treabă! 🤖"]
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
                subprocess.run(["git", "commit", "-m", "Zibi stie cine este creatorul lui! 🛠️"])
                subprocess.run(["git", "push", "origin", "main"])
        except: pass

zibi = ZibiBrain()

def alege_unic(lista):
    disp = [o for o in lista if o not in istoric_raspunsuri]
    ales = random.choice(disp if disp else lista)
    istoric_raspunsuri.append(ales)
    return ales

def cauta_logica_avansata(text_user):
    text_mic = text_user.lower().strip()
    
    # 1. Căutare exactă (Cea mai rapidă)
    if text_mic in zibi.memorie:
        return alege_unic(zibi.memorie[text_mic])

    # 2. Scanare prin cuvinte cheie (Dacă propoziția e lungă)
    # Verificăm dacă întrebarea învățată se regăsește în ce a scris userul
    for intrebare_invatata in zibi.memorie.keys():
        if intrebare_invatata in text_mic and len(intrebare_invatata) > 3:
            return alege_unic(zibi.memorie[intrebare_invatata])

    # 3. Căutare aproximativă (Dacă a scris greșit un cuvânt)
    chei = list(zibi.memorie.keys())
    match = get_close_matches(text_mic, chei, n=1, cutoff=0.6)
    if match:
        return alege_unic(zibi.memorie[match[0]])

    return "🤔 Nu am asta în memorie. Învață-mă: /invata " + text_mic + " : răspuns"

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    if uid == ID_STAPAN:
        if text_mic == "/reset_total":
            zibi.memorie = zibi.default_mem.copy()
            zibi.tokens = 0
            zibi.salveaza()
            return "💥 RESETARE! Acum Zibi știe doar de Brut Studio."

        if text_mic.startswith("/invata"):
            linii = text_raw.split('\n')
            ok = 0
            for linie in linii:
                if ":" in linie:
                    try:
                        # Curățăm comanda /invata și extragem datele
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
                return f"✅ Brut Studio, am memorat {ok} răspunsuri noi!"

    return cauta_logica_avansata(text_raw)

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    bot.reply_to(message, proceseaza_mesaj(message.text, message.from_user.id))

if __name__ == "__main__":
    bot.polling(none_stop=True)
