import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- LOGGER TANIMLAMASI (Hatanı çözen kısım burası) ---
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AYARLAR ---
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
GRUP_ID = -1003991253158
PARTI_GRUP_ID = -1003991253158 
PARTI_KONU_ID = 2  

PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
AKTIF_PARTI_TARIHI = None

# --- YÖNETİCİ MENÜSÜ ---
async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    menu = ("🛠 **Yönetici Menüsü**\n\n"
            "/partibaslat - Parti etkinliği başlat\n"
            "/partiiptal - Etkinliği iptal et\n"
            "/partilistesi - Listeyi dosya olarak al\n"
            "/temizle - Sohbet geçmişini temizle")
    await update.message.reply_text(menu, parse_mode="Markdown")

async def temizle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    
    if update.effective_chat.type == "private":
        if update.effective_user.id in KULLANICI_DURUMLARI:
            KULLANICI_DURUMLARI[update.effective_user.id] = {}
            await update.message.reply_text("🤖 Hafıza temizlendi.")
    else:
        for i in range(1, 50):
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id - i)
            except: break
        await update.message.reply_text("✅ Grup mesajları temizlendi.")

async def parti_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "TARIH_BEKLIYOR"}
    await update.message.reply_text("📅 Partinin tarihini girin (Örn: 15 Haziran):")

async def parti_iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    global AKTIF_PARTI_TARIHI
    if not AKTIF_PARTI_TARIHI:
        await update.message.reply_text("⚠️ Aktif parti yok.")
        return
    await context.bot.send_message(chat_id=PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID,
        text=f"🚫 {AKTIF_PARTI_TARIHI} tarihli parti organizasyonu yöneticilerin kararı ile iptal edilmiştir.")
    AKTIF_PARTI_TARIHI = None
    await update.message.reply_text("✅ Parti iptal edildi.")

async def parti_listesi_dosya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    if not PARTI_LISTESI:
        await update.message.reply_text("📋 Liste boş.")
        return
    sirali = sorted(PARTI_LISTESI.items(), key=lambda x: x[1]['sayi'], reverse=True)
    dosya_icerik = "OYUNCU İSMİ - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in sirali])
    bio = io.BytesIO(dosya_icerik.encode()); bio.name = "parti_listesi.txt"
    await update.message.reply_document(document=InputFile(bio), caption="📋 Güncel parti listesi.")

# --- MAIN FONKSİYONU ---
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CommandHandler("partibaslat", parti_baslat))
    app.add_handler(CommandHandler("partiiptal", parti_iptal))
    app.add_handler(CommandHandler("partilistesi", parti_listesi_dosya))
    app.add_handler(CommandHandler("temizle", temizle))
    
    logger.info("✅ Bot aktif!")
    app.run_polling()

if __name__ == "__main__":
    main()
