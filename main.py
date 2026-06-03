import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN bulunamadı")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if update.message.text.lower().startswith("iyi"):
            await update.message.reply_text("IYI aktif 👀")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for user in update.message.new_chat_members:
            await update.message.reply_text(
                f"Hoş geldin {user.first_name} 🎉"
            )

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

print("Bot çalışıyor...")
app.run_polling()
