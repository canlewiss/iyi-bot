import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import io

# --- LOGGING ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
PARTI_GRUP_ID = -1003991253158
PARTI_KONU_ID = 2

# --- GLOBAL DATA ---
PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
AKTIF_PARTI_TARIHI = None
YASAKLI_KELIMELER = {"küfür1", "argo1", "pislik", "aq", "lan"}

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Merhaba {user.first_name}! Bot başarıyla çalışıyor 🚀 /menu")

async def kayit_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "ISIM"}
    await update.message.reply_text("🎮 Oyun içi isminiz nedir?")

async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    kb = [[InlineKeyboardButton("🎉 Parti Kur", callback_data="kur")],
          [InlineKeyboardButton("🚫 İptal", callback_data="iptal")],
          [InlineKeyboardButton("📋 Liste", callback_data="liste")]]
    await update.message.reply_text("🛠 YÖNETİCİ PANELİ", reply_markup=InlineKeyboardMarkup(kb))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AKTIF_PARTI_TARIHI
    query = update.callback_query
    await query.answer()
    
    if query.data == "kur":
        KULLANICI_DURUMLARI[query.from_user.id] = {"durum": "TARIH"}
        await query.edit_message_text("📅 Tarihi girin (Örn: 10 Haziran):")
    
    elif query.data == "onay_kur":
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=kayit"
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🎉 **{AKTIF_PARTI_TARIHI}** için parti! /kayit yaz veya tıkla:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kayıt Ol", url=bot_url)]]))
        await query.edit_message_text("✅ Etkinlik başlatıldı.")
    
    elif query.data == "liste":
        if not PARTI_LISTESI: await query.edit_message_text("📋 Liste boş.")
        else:
            txt = "\n".join([f"{v['isim']}: {v['sayi']} Parti" for v in PARTI_LISTESI.values()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))
            await query.edit_message_text("✅ Liste gönderildi.")

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AKTIF_PARTI_TARIHI
    uid = update.effective_user.id
    txt = update.message.text
    
    if any(k in txt.lower() for k in YASAKLI_KELIMELER):
        await update.message.delete()
        return

    if uid in KULLANICI_DURUMLARI:
        durum = KULLANICI_DURUMLARI[uid]["durum"]
        if durum == "TARIH":
            AKTIF_PARTI_TARIHI = txt
            kb = [[InlineKeyboardButton("✅ Onayla", callback_data="onay_kur")]]
            await update.message.reply_text(f"📅 '{txt}' onaylıyor musun?", reply_markup=InlineKeyboardMarkup(kb))
            del KULLANICI_DURUMLARI[uid]
        elif durum == "ISIM":
            KULLANICI_DURUMLARI[uid] = {"durum": "SAYI", "isim": txt}
            await update.message.reply_text("🔢 Kaç parti vereceksin?")
        elif durum == "SAYI" and txt.isdigit():
            PARTI_LISTESI[uid] = {"isim": KULLANICI_DURUMLARI[uid]["isim"], "sayi": int(txt)}
            await update.message.reply_text("✅ Kayıt başarılı!")
            del KULLANICI_DURUMLARI[uid]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", kayit_baslat))
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT, mesaj_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
