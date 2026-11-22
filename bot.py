import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import AsyncOpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men sun'iy intellekt yordamchisiman. "
        "Menga istalgan savolingizni o'zbek tilida yozishingiz mumkin."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    histories.pop(update.effective_user.id, None)
    await update.message.reply_text("Suhbat tarixi tozalandi. Yangi suhbat boshlaymiz!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in histories:
        histories[user_id] = []

    histories[user_id].append({"role": "user", "content": message})
    histories[user_id] = histories[user_id][-20:]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sen aqlli, samimiy va foydali AI yordamchisan. "
                    "Foydalanuvchiga asosan o'zbek tilida javob ber. "
                    "Savollarga tushunarli, aniq va tabiiy javob ber."
                },
                *histories[user_id]
            ]
        )

        answer = response.choices[0].message.content
        histories[user_id].append({"role": "assistant", "content": answer})

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("Hozir javob berishda xatolik yuz berdi. Keyinroq urinib ko'ring.")

app = Application.builder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
