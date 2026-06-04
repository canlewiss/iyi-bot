```python
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import io

# Basit Konfigürasyon
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]

logging.basicConfig(level=logging.INFO)

# Veri deposu
data = {
    "list": {},
    "state": {},
    "yasak": ["aq", "amk", "oç", "piç", "lan"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif. /kayit veya /menu")

async def kayit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data["state"][update.effective_user.id] = "ISIM"
    await update.message.reply_text("İsminizi yazın:")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    kb = [[InlineKeyboardButton("Liste", callback_data="liste")]]
    await update.message.reply_text("Menu:", reply_markup=InlineKeyboardMarkup(kb))

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "liste":
        if not data["list"]: await q.edit_message_text("Liste boş.")
        else:
            txt = "\n".join([f"{v['isim']}: {v['sayi']}" for v in data["list"].values()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await q.message.reply_document(document=InputFile(bio))

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    if any(x in txt.lower() for x in data["yasak"]):
        await update.message.delete()
        return
    if uid in data["state"]:
        step = data["state"][uid]
        if step == "ISIM":
            data["state"][uid] = {"step": "SAYI", "isim": txt}
            await update.message.reply_text("Kaç parti?")
        elif isinstance(step, dict) and step["step"] == "SAYI":
            data["list"][uid] = {"isim": step["isim"], "sayi": txt}
            await update.message.reply_text("Kaydedildi!")
            del data["state"][uid]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", kayit))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    app.run_polling()

```
