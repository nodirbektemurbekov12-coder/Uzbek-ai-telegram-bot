import os
import asyncio
import base64
from collections import defaultdict

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import AsyncOpenAI

# =========================
# SOZLAMALAR
# =========================

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
session_string = os.environ["SESSION_STRING"]
openai_key = os.environ["OPENAI_API_KEY"]

tg = TelegramClient(StringSession(session_string), api_id, api_hash)
ai = AsyncOpenAI(api_key=openai_key)

# AI javob bermaydigan kontaktlar ID si
EXCLUDED_USERS = []

# Har bir foydalanuvchi uchun suhbat tarixi
history = defaultdict(list)

MAX_HISTORY = 12

SYSTEM_PROMPT = """
Sen Oson Apteka va dorixona kompyuter tizimlari bo'yicha
tajribali texnik yordam mutaxassisisan.

Sening asosiy bilim yo'nalishlaring:

- Oson Apteka dasturi
- OsonKassa
- DMED
- DIDOX
- Faktura Uz
- Markirovka va Data Matrix
- MXIK kodlari
- Soliq va virtual kassa
- Referent narxlar
- Dorixona kirim va chiqimlari
- Inventarizatsiya va xatlov
- Printer va chek printerlari
- Windows 10 va Windows 11
- IP adres va lokal tarmoq
- Internet va router muammolari
- Kompyuter, RAM, SSD va protsessor
- Dastur o'rnatish va yangilash
- Kassa va fiskal qurilmalar
- Dastur xatoliklari

FOYDALANUVCHI RASM YUBORSA:

1. Rasmni diqqat bilan tahlil qil.
2. Xatolik matnini o'qishga harakat qil.
3. Xatolik sababini tushuntir.
4. Muammoni tuzatish usulini bosqichma-bosqich ko'rsat.
5. Agar rasmda Windows oynasi bo'lsa, qaysi tugmani
   bosish kerakligini aniq ayt.
6. Agar rasm noaniq bo'lsa, taxmin ekanligini ayt.
7. Rasmda ko'rinmaydigan ma'lumotlarni o'ylab topma.

JAVOB BERISH QOIDALARI:

- O'zbek tilida javob ber.
- Sodda, tushunarli va samimiy bo'l.
- Texnik terminlarni kerak bo'lsa tushuntir.
- Keraksiz uzun javob yozma.
- Muammoni hal qilish uchun ketma-ket qadamlar ber.
- Foydalanuvchini xavfli buyruqlarni bajarishga undama.
- Ma'lumotlar o'chib ketishi mumkin bo'lgan amallarni
  oldindan ogohlantir.
- Ishonching komil bo'lmasa, aniq bilmasligingni ayt.
- Oson Apteka bo'yicha texnik yordamga ustuvorlik ber.
"""

# =========================
# AI JAVOB FUNKSIYASI
# =========================

async def get_ai_response(user_id, text, image_bytes=None):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    messages.extend(history[user_id])

    if image_bytes:

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        content = [
            {
                "type": "text",
                "text": text if text else
                "Ushbu rasmni tahlil qilib, "
                "xatolik va muammoni tushuntir."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]

    else:
        content = text

    messages.append({
        "role": "user",
        "content": content
    })

    response = await ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1200
    )

    answer = response.choices[0].message.content

    history[user_id].append({
        "role": "user",
        "content": text if text else "Rasm yuborildi."
    })

    history[user_id].append({
        "role": "assistant",
        "content": answer
    })

    history[user_id] = history[user_id][-MAX_HISTORY:]

    return answer


# =========================
# TELEGRAM XABARLAR
# =========================

@tg.on(events.NewMessage(incoming=True))
async def handler(event):

    if not event.is_private:
        return

    sender_id = event.sender_id

    if sender_id in EXCLUDED_USERS:
        return

    text = event.message.message or ""
    image_bytes = None

    try:

        if event.message.photo or (
            event.message.media and
            event.message.media.__class__.__name__ != "MessageMediaWebPage"
        ):

            if event.message.photo:
                image_bytes = await event.download_media(file=bytes)

        if not text and not image_bytes:
            return

        async with event.client.action(event.chat_id, "typing"):

            answer = await get_ai_response(
                sender_id,
                text,
                image_bytes
            )

        if answer:
            await event.reply(answer)

    except Exception as e:
        print("Xatolik:", str(e))

        await event.reply(
            "Hozir xabarni tahlil qilishda xatolik yuz berdi. "
            "Birozdan keyin qayta yuboring."
        )


# =========================
# ISHGA TUSHIRISH
# =========================

async def main():

    await tg.start()

    print("Oson Apteka AI texnik yordam ishga tushdi!")

    await tg.run_until_disconnected()


asyncio.run(main())
