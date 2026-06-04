import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Loglama Ayarları
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Ayarlar
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
GRUP_ID = -1003991253158
PARTI_GRUP_ID = -1003991253158
PARTI_KONU_ID = 2

# Veri Depoları
PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
YASAKLI_KELIMELER = ["küfür1", "argo1", "hakaret1", "pislik", "kötü", "lan", "aq"]

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] == "kayit":
        KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "ISIM_BEKLIYOR"}
        await update.message.reply_text("🎮 İsminiz nedir?")
    else:
        await update.message.reply_text("👋 Sunday City Etkinlik Botu aktif. Yöneticiler için: /menu")

async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    await update.message.reply_text("🛠 **Yönetici Paneli**\n/partibaslat - Etkinlik kur\n/partilistesi - Dosya al\n/partiiptal - Etkinliği bitir\n/temizle - Geçmişi sil")

async def parti_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
        text="🎉 **SUNDAY CITY PARTİ ETKİNLİĞİ BAŞLIYOR!**\n\n👇 Kayıt için butona tıkla!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Kayıt Ol", url=f"https://t.me/{(await context.bot.get_me()).username}?start=kayit")]]))

async def parti_listesi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    if not PARTI_LISTESI:
        await update.message.reply_text("📋 Liste boş.")
        return
    sirali = sorted(PARTI_LISTESI.items(), key=lambda x: x[1]['sayi'], reverse=True)
    txt = "İSİM - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in sirali])
    txt += f"\n\nTOPLAM PARTİ: {sum(v['sayi'] for v in PARTI_LISTESI.values())}"
    bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
    await update.message.reply_document(document=InputFile(bio))

# --- İŞLEMLER ---
async def mesaj_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.lower() if update.message.text else ""

    # Küfür Filtresi
    if any(k in text for k in YASAKLI_KELIMELER):
        await update.message.delete()
        return

    # Parti Kayıt Akışı
    if uid in KULLANICI_DURUMLARI:
        durum = KULLANICI_DURUMLARI[uid]["durum"]
        if durum == "ISIM_BEKLIYOR":
            KULLANICI_DURUMLARI[uid] = {"durum": "SAYI_BEKLIYOR", "isim": update.message.text}
            await update.message.reply_text("🎮 İsim alındı. Kaç parti vereceksiniz? (Sayı yaz):")
        elif durum == "SAYI_BEKLIYOR" and update.message.text.isdigit():
            PARTI_LISTESI[uid] = {"isim": KULLANICI_DURUMLARI[uid]["isim"], "sayi": int(update.message.text)}
            await update.message.reply_text("✅ Kayıt başarılı!")
            del KULLANICI_DURUMLARI[uid]

async def temizle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    for i in range(50):
        try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id - i)
        except: break

# --- MAIN ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CommandHandler("partibaslat", parti_baslat))
    app.add_handler(CommandHandler("partilistesi", parti_listesi))
    app.add_handler(CommandHandler("temizle", temizle))
    app.add_handler(MessageHandler(filters.TEXT, mesaj_kontrol))
    
    logger.info("✅ Bot tam kapasite aktif!")
    app.run_polling()

if __name__ == "__main__":
    main()
