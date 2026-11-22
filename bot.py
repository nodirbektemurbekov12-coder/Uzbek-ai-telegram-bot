import os
import asyncio
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import AsyncOpenAI

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
session_string = os.environ["SESSION_STRING"]
openai_key = os.environ["OPENAI_API_KEY"]

tg = TelegramClient(StringSession(session_string), api_id, api_hash)
ai = AsyncOpenAI(api_key=openai_key)

last_activity = time.time()
WAIT_TIME = 300  # 3 daqiqa

@tg.on(events.NewMessage(outgoing=True))
async def activity_handler(event):
    global last_activity
    last_activity = time.time()

@tg.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    if event.sender_id == (await tg.get_me()).id:
        return

    # Siz yaqinda faol bo'lgan bo'lsangiz, javob bermaydi
    if time.time() - last_activity < WAIT_TIME:
        return

    msg = event.message.message
    if not msg:
        return

    try:
        response = await ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sen o'zbek tilida tabiiy, samimiy va qisqa javob beradigan yordamchisan. O'zini akkaunt egasi sifatida tut, lekin kerak bo'lsa sun'iy intellekt ekaningni yashirma."
                },
                {"role": "user", "content": msg}
            ]
        )

        answer = response.choices[0].message.content
        await event.reply(answer)

    except Exception as e:
        print("Xatolik:", e)

async def main():
    await tg.start()
    print("Telegram AI ishga tushdi!")
    await tg.run_until_disconnected()

asyncio.run(main())
