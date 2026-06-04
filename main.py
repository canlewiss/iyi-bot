import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Railway panelinde hataları net görebilmek için log ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# DOĞRUDAN EKLENMİŞ TOKEN
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Merhaba {user.first_name}! Bot başarıyla çalışıyor 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcının yazdığını geri gönderen basit bir özellik
    mesaj = update.message.text
    await update.message.reply_text(f"Bunu yazdın: {mesaj}")

def main():
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
