
import os
import json
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

AUTO_REPLY = (
    "Assalomu alaykum! Xabaringizni oldim. "
    "Bo'sh vaqtim bo'lishi bilan sizga javob yozaman. Rahmat! 😊"
)

FILE = "replied_users.json"

def load_users():
    try:
        with open(FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

replied_users = load_users()

def save_users():
    with open(FILE, "w") as f:
        json.dump(list(replied_users), f)

@bot.message_handler(func=lambda message: message.chat.type == "private")
def auto_reply(message):
    if message.text and message.text.startswith("/"):
        return

    user_id = str(message.chat.id)

    if user_id not in replied_users:
        bot.reply_to(message, AUTO_REPLY)
        replied_users.add(user_id)
        save_users()

@app.route("/")
def home():
    return "Bot ishlayapti!"

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
