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

class ZibiBrain:
    def __init__(self):
        self.memorie = {}
        self.tokens = 0
        self.incarca()

    def incarca(self):
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date = json.load(f)
                    self.memorie = {k.lower(): (v if isinstance(v, list) else [v]) for k, v in date.get("date_memorie", {}).items()}
                    self.tokens = date.get("tokens", 0)
            except: self.memorie = {}

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # --- FUNCȚIA DE SALVARE PE GITHUB (AUTO-COMMIT) ---
            # Această parte trimite fișierul înapoi în repository-ul tău
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "ZibiBot-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi a învățat ceva nou! ✨"])
                subprocess.run(["git", "push"])
        except Exception as e:
            print(f"Eroare la salvare: {e}")

zibi = ZibiBrain()

def alege_unic(lista_optiuni):
    if not lista_optiuni: return "🤔..."
    disponibile = [opt for opt in lista_optiuni if opt not in istoric_raspunsuri]
    ales = random.choice(disponibile if disponibile else lista_optiuni)
    istoric_raspunsuri.append(ales)
    return ales

# --- LOGICA DE PROCESARE ---
def proceseaza_mesaj(text_raw, uid):
    text_curat = text_raw.strip()
    linii = text_curat.split('\n')
    text_mic = text_curat.lower()

    # 1. ADMIN: ÎNVĂȚARE / ȘTERGERE
    if text_mic.startswith("/invata") and uid == ID_STAPAN:
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
        zibi.salveaza() # Aici se declanșează salvarea și push-ul pe GitHub
        return f"✨ Am învățat {invatate} variante noi! Totul a fost salvat permanent în baza de date. (Tokens: {zibi.tokens})"

    if text_mic.startswith("/sterge") and uid == ID_STAPAN:
        cuvant = text_mic.replace("/sterge", "").strip()
        if cuvant in zibi.memorie:
            del zibi.memorie[cuvant]
            zibi.salveaza()
            return f"🗑️ Am șters '{cuvant}' și am actualizat serverul."
        return "❓ Nu am găsit categoria."

    # 2. CONVERSAȚIE
    chei = list(zibi.memorie.keys())
    potrivire = get_close_matches(text_mic, chei, n=1, cutoff=0.5)
    if potrivire:
        return alege_unic(zibi.memorie[potrivire[0]])
    
    return "🤔 Nu știu ce să zic la asta. Învață-mă ceva nou!"

# --- TG HANDLER ---
@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    raspuns = proceseaza_mesaj(message.text, message.from_user.id)
    bot.reply_to(message, raspuns)

if __name__ == "__main__":
    print("Zibi este online cu sistem de salvare permanentă!")
    bot.polling(none_stop=True)
