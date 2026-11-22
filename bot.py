
import os
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta, timezone

from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

AUTO_REPLY = os.getenv(
    "AUTO_REPLY",
    "Assalomu alaykum! Xabaringizni oldim. Vaqtim bo‘lishi bilan sizga javob yozaman."
)

COOLDOWN_HOURS = 24
DB_FILE = os.getenv("DB_FILE", "replies.db")

db = sqlite3.connect(DB_FILE, check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS replies (
    user_id INTEGER PRIMARY KEY,
    last_reply TEXT NOT NULL
)
""")
db.commit()

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        if not event.is_private:
            return

        sender = await event.get_sender()

        if sender.bot or sender.id == (await client.get_me()).id:
            return

        now = datetime.now(timezone.utc)

        row = db.execute(
            "SELECT last_reply FROM replies WHERE user_id = ?",
            (sender.id,)
        ).fetchone()

        if row:
            last = datetime.fromisoformat(row[0])

            if now - last < timedelta(hours=COOLDOWN_HOURS):
                logging.info("24 soatlik limit: %s", sender.id)
                return

        await event.respond(AUTO_REPLY)

        db.execute(
            "INSERT OR REPLACE INTO replies (user_id, last_reply) VALUES (?, ?)",
            (sender.id, now.isoformat())
        )
        db.commit()

        logging.info("JAVOB YUBORILDI: %s", sender.id)

    except Exception:
        logging.exception("Xabarni qayta ishlashda xato")


async def main():
    await client.start()
    me = await client.get_me()

    logging.info("Telegram ulandi: %s", me.id)
    logging.info("Avtomatik javob faol.")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
