
import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

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

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not event.is_private:
        return

    if event.sender_id is None:
        return

    sender = await event.get_sender()

    if sender is None or getattr(sender, "bot", False):
        return

    try:
        await event.reply(AUTO_REPLY)
        print(f"Auto reply yuborildi: {event.sender_id}")
    except Exception as e:
        print(f"Xatolik: {e}")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"AKKAUNT ISHLAYAPTI: {me.id}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
