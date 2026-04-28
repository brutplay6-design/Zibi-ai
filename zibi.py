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
        # 1. REPLICI DE BAZĂ (Acestea nu se șterg niciodată)
        self.default_mem = {
            "salut": ["Salut! Sunt asistentul Brut Studio. 🌟"],
            "cine te-a creat": ["Creatorul meu este Brut Studio! 🚀"],
            "ce faci": ["Sunt online și gata de treabă! 🤖"]
        }
        self.memorie = self.default_mem.copy()
        self.tokens = 0
        self.incarca_si_combina() # Folosim funcția nouă de combinare

    def incarca_si_combina(self):
        """Încarcă memoria veche și o unește cu cea nouă, fără ștergeri."""
        if os.path.exists(FISIER_MEMORIE):
            try:
                with open(FISIER_MEMORIE, "r", encoding="utf-8") as f:
                    date_vechi = json.load(f)
                    if "date_memorie" in date_vechi:
                        mem_veche = date_vechi["date_memorie"]
                        # Unim memoriile: adăugăm ce e nou peste ce e vechi
                        for q, r_list in mem_veche.items():
                            q_clean = q.strip().lower()
                            if q_clean not in self.memorie:
                                self.memorie[q_clean] = r_list
                            else:
                                # Dacă întrebarea există deja, unim listele de răspunsuri fără duplicate
                                self.memorie[q_clean] = list(set(self.memorie[q_clean] + r_list))
                        
                        self.tokens = date_vechi.get("tokens", 0)
                print("✅ Memoria a fost combinată cu succes!")
            except Exception as e:
                print(f"⚠️ Eroare la combinare: {e}")

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # PUSH PE GITHUB (Salvare permanentă în Cloud)
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi și-a păstrat amintirile! 🧠"])
                subprocess.run(["git", "push", "origin", "main"])
        except: pass

zibi = ZibiBrain()

# --- LOGICĂ CONVERSAȚIE ---
def alege_unic(lista):
    disp = [o for o in lista if o not in istoric_raspunsuri]
    ales = random.choice(disp if disp else lista)
    istoric_raspunsuri.append(ales)
    return ales

def proceseaza_mesaj(text_raw, uid):
    text_mic = text_raw.strip().lower()
    
    if uid == ID_STAPAN:
        if text_mic == "/reset_total":
            zibi.memorie = zibi.default_mem.copy()
            zibi.tokens = 0
            zibi.salveaza()
            return "💥 MEMORIE RESETATĂ LA ZERO!"

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
                return f"✅ Brut Studio, am memorat {ok} lucruri noi!"

    # Căutare inteligentă
    if text_mic in zibi.memorie:
        return alege_unic(zibi.memorie[text_mic])
    
    chei = list(zibi.memorie.keys())
    match = get_close_matches(text_mic, chei, n=1, cutoff=0.5)
    if match:
        return alege_unic(zibi.memorie[match[0]])

    return "🤔 Nu știu asta. Învață-mă: /invata intrebare : raspuns"

@bot.message_handler(func=lambda m: True)
def tg_msg(message):
    bot.reply_to(message, proceseaza_mesaj(message.text, message.from_user.id))

if __name__ == "__main__":
    bot.polling(none_stop=True)
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
