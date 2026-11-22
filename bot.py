import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import AsyncOpenAI

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
session_string = os.environ["SESSION_STRING"]
openai_key = os.environ["OPENAI_API_KEY"]

tg = TelegramClient(StringSession(session_string), api_id, api_hash)
ai = AsyncOpenAI(api_key=openai_key)

@tg.on(events.NewMessage(incoming=True, from_users=None))
async def handler(event):
    if not event.is_private:
        return

    if event.sender_id == (await tg.get_me()).id:
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
                    "content": "Sen o'zbek tilida tabiiy, samimiy va qisqa javob beradigan AI yordamchisan. Suhbatni erkin olib bor."
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
