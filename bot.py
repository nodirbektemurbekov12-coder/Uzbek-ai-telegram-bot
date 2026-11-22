
import os
import asyncio
import base64

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import AsyncOpenAI

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
session_string = os.environ["SESSION_STRING"]
openai_key = os.environ["OPENAI_API_KEY"]

tg = TelegramClient(StringSession(session_string), api_id, api_hash)
ai = AsyncOpenAI(api_key=openai_key)

EXCLUDED_USERS = []

SYSTEM_PROMPT = """
Sen Oson Apteka, OsonKassa, DMED, markirovka,
MXIK, printer, Windows va kompyuter tarmoqlari
bo'yicha texnik yordamchi mutaxassissan.

O'zbek tilida sodda, tushunarli va samimiy javob ber.

Foydalanuvchi screenshot yoki rasm yuborsa,
rasmdagi yozuvlar, xatolik kodlari va interfeysni
tahlil qil. Xatoni aniqlashga harakat qil.

Yechimni bosqichma-bosqich tushuntir.
Bir vaqtning o'zida juda ko'p qadam bermagin.
Avval eng ehtimoliy va xavfsiz yechimni ko'rsat.

Agar xato aniq bo'lmasa, taxmin ekanligini ayt.
Ma'lumotni o'ylab topma.
Foydalanuvchidan keyingi natijani so'rab,
muammoni ketma-ket hal qil.

Dori vositalarining klinik tavsiyalarini bermagin.
Texnik yordam bilan cheklan.
"""

@tg.on(events.NewMessage(incoming=True))
async def handler(event):

    if not event.is_private:
        return

    if event.sender_id in EXCLUDED_USERS:
        return

    msg = event.message.message or ""

    try:

        if event.message.photo or (
            event.message.document and
            event.message.document.mime_type and
            event.message.document.mime_type.startswith("image/")
        ):

            image_bytes = await event.message.download_media(
                file=bytes
            )

            if not image_bytes:
                await event.reply("Rasmni yuklab ololmadim. Qayta yuboring.")
                return

            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            mime_type = "image/jpeg"

            if event.message.document:
                mime_type = event.message.document.mime_type

            response = await ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": msg or "Ushbu rasmni tahlil qil va xatoni tushuntir."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ]
            )

        else:

            if not msg:
                return

            response = await ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": msg
                    }
                ]
            )

        answer = response.choices[0].message.content

        if answer:
            await event.reply(answer)

    except Exception as e:
        print("Xatolik:", e)


async def main():
    await tg.start()
    print("Oson Apteka AI ishga tushdi!")
    await tg.run_until_disconnected()


asyncio.run(main())
