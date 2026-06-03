import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN eksik")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("IYI bot çalışıyor 👀")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

print("Bot başladı")
app.run_polling()
