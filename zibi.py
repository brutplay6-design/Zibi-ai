import telebot
import json
import os
import random
import subprocess
from difflib import get_close_matches

TOKEN = "8276199135:AAGTcsdHJdncH_UZsv5PzSHFDGCzkOGibt8"
ID_STAPAN = 7040347167 
bot = telebot.TeleBot(TOKEN)
FISIER_MEMORIE = "zibi_memorie.json"

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
                    # Încărcăm tot ce este în JSON
                    self.memorie = {k.lower(): v for k, v in date.get("date_memorie", {}).items()}
                    self.tokens = date.get("tokens", 0)
            except: self.memorie = {}

    def salveaza(self):
        try:
            with open(FISIER_MEMORIE, "w", encoding="utf-8") as f:
                json.dump({"date_memorie": self.memorie, "tokens": self.tokens}, f, ensure_ascii=False, indent=4)
            
            # Salvare automată pe GitHub dacă suntem în Actions
            if os.getenv("GITHUB_ACTIONS"):
                subprocess.run(["git", "config", "user.name", "Zibi-AutoSave"])
                subprocess.run(["git", "config", "user.email", "bot@zibi.com"])
                subprocess.run(["git", "add", FISIER_MEMORIE])
                subprocess.run(["git", "commit", "-m", "Zibi și-a mărit memoria! 🧠"])
                subprocess.run(["git", "push"])
        except: pass

zibi = ZibiBrain()

@bot.message_handler(commands=['invata'])
def invata_command(message):
    if message.from_user.id != ID_STAPAN:
        bot.reply_to(message, "🚫 Doar șeful meu mă poate învăța!")
        return

    text = message.text.replace("/invata", "").strip()
    if ":" in text:
        intrebare, raspuns = text.split(":", 1)
        intrebare = intrebare.strip().lower()
        raspuns = raspuns.strip()

        if intrebare not in zibi.memorie: zibi.memorie[intrebare] = []
        zibi.memorie[intrebare].append(raspuns)
        zibi.tokens += 10
        zibi.salveaza()
        bot.reply_to(message, f"✅ Am învățat! Acum am {len(zibi.memorie)} subiecte în memorie.")
    else:
        bot.reply_to(message, "❌ Folosește: /invata intrebare : raspuns")

@bot.message_handler(func=lambda m: True)
def chat(message):
    text = message.text.lower().strip()
    chei = list(zibi.memorie.keys())
    
    # Caută cea mai apropiată potrivire în cele 700+ de memorii
    potrivire = get_close_matches(text, chei, n=1, cutoff=0.4)
    
    if potrivire:
        bot.reply_to(message, random.choice(zibi.memorie[potrivire[0]]))
    else:
        bot.reply_to(message, "🤔 Nu am asta în cele 700 de memorii. Învață-mă cu /invata!")

if __name__ == "__main__":
    bot.polling(none_stop=True)
