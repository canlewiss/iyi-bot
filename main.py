import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Railway panelinde hataları net görebilmek için log ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway'den TOKEN'ı çekiyoruz
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Merhaba {user.first_name}! Bot başarıyla çalışıyor 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcının yazdığını geri gönderen basit bir özellik
    mesaj = update.message.text
    await update.message.reply_text(f"Bunu yazdın: {mesaj}")

def main():
    # Eğer Railway TOKEN'ı okuyamazsa sessizce çökmek yerine konsola uyarı basacak
    if not TOKEN:
        logger.error("🚨 HATA: TOKEN bulunamadı! Lütfen Railway 'Variables' sekmesini kontrol et.")
        return

    # Bot uygulamasını oluştur
    app = Application.builder().token(TOKEN).build()

    # Komutları bota tanıt
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("✅ Bot başarıyla ayağa kalktı ve mesajları dinliyor...")
    
    # Botu sürekli çalışır halde tut
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
