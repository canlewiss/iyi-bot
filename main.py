import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- AYARLAR ---
# Token'ı tırnakların içine yapıştır
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = {7924242319, 1293227694, 5656861374}
PARTI_GRUP_ID = -1003991253158

logging.basicConfig(level=logging.INFO)

# --- VERİ YAPISI ---
class AppData:
    def __init__(self):
        self.parti_list = {}
        self.user_state = {}
        self.event_date = None
        self.yasakli = {"aq", "amk", "oç", "piç", "lan"}

app_data = AppData()

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Merhaba {update.effective_user.first_name}! Bot aktif 🚀")

async def kayit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app_data.user_state[update.effective_user.id] = "ISIM_BEKLIYOR"
    await update.message.reply_text("🎮 İsminiz nedir?")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    kb = [[InlineKeyboardButton("🎉 Parti Kur", callback_data="kur")],
          [InlineKeyboardButton("📋 Liste", callback_data="liste")]]
    await update.message.reply_text("🛠 Admin Panel", reply_markup=InlineKeyboardMarkup(kb))

# --- İŞLEMCİLER ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "kur":
        app_data.user_state[query.from_user.id] = "TARIH_BEKLIYOR"
        await query.edit_message_text("📅 Tarih girin:")
    elif query.data == "liste":
        if not app_data.parti_list: await query.edit_message_text("Liste boş.")
        else:
            txt = "\n".join([f"{v['isim']}: {v['sayi']} Parti" for v in app_data.parti_list.values()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    
    if any(k in txt.lower() for k in app_data.yasakli):
        await update.message.delete()
        return

    if uid in app_data.user_state:
        state = app_data.user_state[uid]
        if state == "TARIH_BEKLIYOR":
            app_data.event_date = txt
            await update.message.reply_text(f"✅ '{txt}' olarak kaydedildi.")
            del app_data.user_state[uid]
        elif state == "ISIM_BEKLIYOR":
            app_data.user_state[uid] = {"state": "SAYI_BEKLIYOR", "isim": txt}
            await update.message.reply_text("🔢 Kaç parti?")
        elif state["state"] == "SAYI_BEKLIYOR":
            app_data.parti_list[uid] = {"isim": state["isim"], "sayi": txt}
            await update.message.reply_text("✅ Kayıt başarılı!")
            del app_data.user_state[uid]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", kayit))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot başlatılıyor...")
    app.run_polling()
