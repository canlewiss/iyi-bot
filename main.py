import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise Exception("TOKEN bulunamadı! Render Environment Variables kontrol et.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if update.message.text.lower().startswith("iyi"):
            await update.message.reply_text("IYI aktif 👀")

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("IYI bot çalışıyor...")
app.run_polling()
