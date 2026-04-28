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

# --- EVITARE REPETARE ---
istoric_raspunsuri = deque(maxlen=10)

# --- CREIER DEFAULT (Ca să răspundă mereu la salut și glume) ---
MEMORIE_DEFAULT = {
    "salut": ["Salutare! Sper că ai o zi grozavă! 🌟", "Opa, a venit șeful! 😎", "Salut! 🍕"],
    "sal": ["Salut! Ce mai zici? 👋", "Sall! Bine ai venit! ✨"],
    "ce faci": ["Îmi număr degetele invizibile. Tu? 🖐️", "Mă gândeam la un plan de cucerit frigiderul. 🍗"],
    "gluma": ["De ce are rinocerul corn? Ca să nu pară un hipopotam supărat! 🦏", "Ce face o vacă pe lună? Muuu-nwalk! 🐄"],
    "cum te numesti": ["Numele meu este Zibi, cel mai tare bot de pe GitHub! 🤖"]
}

class ZibiBrain:
    def __init__(self):
        self.memorie = MEMORIE_DEFAULT.copy() # Începe cu salutările de bază
        self.tokens = 0
        self.incarca()

    def incarca(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    date_incarcate = {k.lower(): (v if isinstance(v, list) else [v]) for k, v in date.get("date_memorie", {}).items()}
                    self.memorie.update(date_incarcate) # Adaugă ce a învățat peste baza de date
                    self.tokens = date.get("tokens", 0)
            except: pass

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # AUTO-SAVE PE GITHUB (Dacă ai dat permisiunile de Write în Settings)
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "ZibiBot-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi a învățat ceva nou! ✨"])
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
    
    # 1. ÎNVĂȚARE / ȘTERGERE (Doar tu)
    if text_mic.startswith("/invata") and uid == ID_STAPAN:
        linii = text_raw.split('\n')
        invatate = 0
        for linie in linii:
            if ":" in linie:
                piese = linie.split(":", 1)
                intrebare = piese[0].lower().replace("/invata", "").strip()
                raspuns = piese[1].strip()
                if intrebare not in zibi.memorie: zibi.memorie[intrebare] = []
                if raspuns not in zibi.memorie[intrebare]:
                    zibi.memorie[intrebare].append(raspuns)
                    zibi.tokens += 10
                    invatate += 1
        zibi.salveaza()
        return f"✨ Am învățat {invatate} lucruri! (Tokens: {zibi.tokens})"

    # 2. CONVERSAȚIE (Pentru toată lumea)
    chei = list(zibi.memorie.keys())
    potrivire = get_close_matches(text_mic, chei, n=1, cutoff=0.5)
    
    if potrivire:
        return alege_unic(zibi.memorie[potrivire[0]])
    
    return "🤔 Nu știu ce să zic la asta. Învață-mă: /invata intrebare : raspuns"

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    raspuns = proceseaza_mesaj(message.text, message.from_user.id)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    print("Zibi e online!")
    bot.polling(none_stop=True)
