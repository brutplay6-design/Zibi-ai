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
        self.memorie = {
            "salut": ["Salutare! 🌟", "Hei! 😎"],
            "gluma": ["Ce face o vacă pe lună? Muuu-nwalk! 🐄"]
        }
        self.tokens = 0
        self.incarca()

    def incarca(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    if "date_memorie" in date:
                        for k, v in date["date_memorie"].items():
                            self.memorie[k.lower()] = v if isinstance(v, list) else [v]
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
                subprocess.run(["git", "commit", "-m", f"Zibi a invatat pachet nou! Tokens: {self.tokens}"])
                subprocess.run(["git", "push"])
        except: pass

zibi = ZibiBrain()

def alege_unic(lista_optiuni):
    disponibile = [opt for opt in lista_optiuni if opt not in istoric_raspunsuri]
    ales = random.choice(disponibile if disponibile else lista_optiuni)
    istoric_raspunsuri.append(ales)
    return ales

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    # --- FUNCȚIA DE ÎNVĂȚARE RAPIDĂ (MULTI-LINE) ---
    if text_mic.startswith("/invata") and uid == ID_STAPAN:
        linii = text_raw.split('\n')
        total_invatate = 0
        
        for linie in linii:
            linie_curata = linie.replace("/invata", "").strip()
            if ":" in linie_curata:
                try:
                    intrebare, raspuns = linie_curata.split(":", 1)
                    q = intrebare.strip().lower()
                    r = raspuns.strip()
                    
                    if q not in zibi.memorie: zibi.memorie[q] = []
                    if r not in zibi.memorie[q]:
                        zibi.memorie[q].append(r)
                        zibi.tokens += 10
                        total_invatate += 1
                except: continue
        
        if total_invatate > 0:
            zibi.salveaza()
            return f"🚀 Super viteza! Am învățat {total_invatate} lucruri noi dintr-o dată! (Total Tokens: {zibi.tokens})"
        return "❌ Nu am găsit formatul corect. Scrie 'intrebare : raspuns' pe fiecare rând."

    # --- RĂSPUNS AUTOMAT ---
    chei = list(zibi.memorie.keys())
    potrivire = get_close_matches(text_mic, chei, n=1, cutoff=0.5)
    if potrivire:
        return alege_unic(zibi.memorie[potrivire[0]])
    
    return "🤔 Nu știu asta. Folosește /invata ca să mă deștepți!"

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    raspuns = proceseaza_mesaj(message.text, message.from_user.id)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    bot.polling(none_stop=True)
