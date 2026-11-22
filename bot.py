import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

AUTO_REPLY = os.getenv(
    "AUTO_REPLY",
    "Assalomu alaykum! Xabaringizni oldim. Tez orada javob beraman."
)

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

replied_users = set()

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    sender = await event.get_sender()

    if getattr(sender, "bot", False):
        return

    uid = event.sender_id

    if uid in replied_users:
        return

    try:
        await event.respond(AUTO_REPLY)
        replied_users.add(uid)
        logging.info(f"JAVOB YUBORILDI: {uid}")

    except Exception as e:
        logging.error(f"XATOLIK: {e}")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"BOT ISHLAYAPTI: {me.id}")
    await client.run_until_disconnected()

asyncio.run(main())
