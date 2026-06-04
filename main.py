import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Loglama
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Ayarlar
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
PARTI_GRUP_ID = -1003991253158
PARTI_KONU_ID = 2

# Veri
PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
AKTIF_PARTI_TARIHI = None
YASAKLI_KELIMELER = ["küfür1", "argo1", "pislik", "aq", "lan"]

# --- YÖNETİCİ KOMUTLARI ---
async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    keyboard = [
        [InlineKeyboardButton("🎉 Parti Başlat", callback_data="admin_baslat")],
        [InlineKeyboardButton("🚫 Parti İptal", callback_data="admin_iptal")],
        [InlineKeyboardButton("📋 Listeyi Al", callback_data="admin_liste")],
        [InlineKeyboardButton("🧹 Temizle", callback_data="admin_temizle")]
    ]
    await update.message.reply_text("🛠 **Yönetici Paneli**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- İŞLEMLER ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    if uid not in YONETICILER: return

    if query.data == "admin_baslat":
        KULLANICI_DURUMLARI[uid] = {"durum": "TARIH_BEKLIYOR"}
        await query.edit_message_text("📅 Partinin tarihini yazın (Örn: 10 Haziran 20:00):")

    elif query.data == "admin_iptal":
        global AKTIF_PARTI_TARIHI
        if not AKTIF_PARTI_TARIHI:
            await query.edit_message_text("⚠️ Aktif parti yok.")
            return
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🚫 {AKTIF_PARTI_TARIHI} tarihli parti organizasyonu yöneticilerin ortak kararı ile iptal edilmiştir.")
        AKTIF_PARTI_TARIHI = None
        await query.edit_message_text("✅ İptal edildi.")

    elif query.data == "admin_liste":
        if not PARTI_LISTESI:
            await query.edit_message_text("📋 Liste boş.")
            return
        sirali = sorted(PARTI_LISTESI.items(), key=lambda x: x[1]['sayi'], reverse=True)
        txt = "İSİM - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in sirali])
        bio = io.BytesIO(txt.encode()); bio.name = "parti_listesi.txt"
        await query.message.reply_document(document=InputFile(bio))

    elif query.data == "admin_temizle":
        PARTI_LISTESI.clear()
        await query.edit_message_text("✅ Liste sıfırlandı.")

# --- MESAJ İŞLEME ---
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid = update.effective_user.id
    text = update.message.text

    # Küfür Filtresi
    if any(k in text.lower() for k in YASAKLI_KELIMELER):
        await update.message.delete()
        return

    # Parti Tarih Onay Akışı
    if uid in KULLANICI_DURUMLARI and KULLANICI_DURUMLARI[uid].get("durum") == "TARIH_BEKLIYOR":
        global AKTIF_PARTI_TARIHI
        AKTIF_PARTI_TARIHI = text
        await update.message.reply_text(f"✅ {text} onaylandı, gruba duyuru atıldı.")
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=kayit"
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🎉 **{text} Parti Etkinliği!**\n👇 Kayıt olmak için butona tıkla!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Kayıt Ol", url=bot_url)]]))
        del KULLANICI_DURUMLARI[uid]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Merhaba BugMaster! 🚀 /menu")))
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT, mesaj_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
