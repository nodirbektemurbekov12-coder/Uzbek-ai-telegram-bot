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
async def main():
    await client.connect()

    if not await client.is_user_authorized():
        print("SESSION_STRING NOT AUTHORIZED")
        return

    me = await client.get_me()
    print(f"BOT ISHLAYAPTI: {me.id}")

    await client.run_until_disconnected()

asyncio.run(main())
