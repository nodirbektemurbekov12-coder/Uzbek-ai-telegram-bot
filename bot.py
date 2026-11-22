
import os
import asyncio
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

AUTO_REPLY = os.getenv(
    "AUTO_REPLY",
    "Assalomu alaykum! Xabaringizni oldim. Tez orada javob beraman."
)

# 24 soat = 86400 sekund
REPLY_INTERVAL = 86400

# Oxirgi javob yuborilgan kontaktlar
replied_users = {}

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not event.is_private:
        return

    sender_id = event.sender_id

    if sender_id is None:
        return

    sender = await event.get_sender()

    if sender is None or getattr(sender, "bot", False):
        return

    now = time.time()
    last_reply = replied_users.get(sender_id, 0)

    # 24 soat ichida yana javob bermaslik
    if now - last_reply < REPLY_INTERVAL:
        print(f"24 soatlik limit: {sender_id}")
        return

    try:
        await event.reply(AUTO_REPLY)
        replied_users[sender_id] = now
        print(f"Auto reply yuborildi: {sender_id}")

    except Exception as e:
        print(f"Xatolik: {e}")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"AKKAUNT ISHLAYAPTI: {me.id}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
