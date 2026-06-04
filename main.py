import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Log ayarları
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
GRUP_ID = -1003991253158
PARTI_GRUP_ID = -1003991253158 
PARTI_KONU_ID = 2  

PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
AKTIF_PARTI_TARIHI = None

# --- YÖNETİCİ KOMUTLARI ---
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
    # Mesajları silmek için döngü (Botun mesaj silme yetkisi olmalı)
    await update.message.reply_text("🧹 Sohbet geçmişi temizleniyor...")
    # Basit bir silme mantığı (son mesajları siler)
    for i in range(100):
        try:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id - i)
        except: break
    await update.message.reply_text("✅ Temizlik tamamlandı.")

async def parti_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "TARIH_BEKLIYOR"}
    await update.message.reply_text("📅 Partinin tarihini girin (Örn: 15 Haziran):")

# --- PARTİ DUYURU (SABİTLEME ÖZELLİĞİ İLE) ---
async def parti_duyuru_gonder(context, tarih):
    bot_username = (await context.bot.get_me()).username
    url = f"https://t.me/{bot_username}?start=parti"
    
    mesaj = (
        "🎉 **SUNDAY CITY PARTİ ETKİNLİĞİ BAŞLIYOR!**\n\n"
        "Etkinliğe katılıp parti vermek isteyen oyuncularımız, aşağıdaki butona tıklayarak "
        "gizli ve güvenli bir şekilde kaydını oluşturabilir.\n\n"
        "👇 Hemen kayıt olmak için butona tıkla!"
    )
    
    klavye = [[InlineKeyboardButton("🎉 Parti Kaydını Başlat", url=url)]]
    msg = await context.bot.send_message(
        chat_id=PARTI_GRUP_ID, 
        message_thread_id=PARTI_KONU_ID,
        text=mesaj, 
        reply_markup=InlineKeyboardMarkup(klavye), 
        parse_mode="Markdown"
    )
    # Sabitleme yetkisi varsa sabitle
    try:
        await context.bot.pin_chat_message(chat_id=PARTI_GRUP_ID, message_id=msg.message_id)
    except: pass

# --- İPTAL KOMUTU ---
async def parti_iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    global AKTIF_PARTI_TARIHI
    if not AKTIF_PARTI_TARIHI:
        await update.message.reply_text("⚠️ Aktif parti yok.")
        return
    
    await context.bot.send_message(
        chat_id=PARTI_GRUP_ID, 
        message_thread_id=PARTI_KONU_ID,
        text=f"🚫 {AKTIF_PARTI_TARIHI} tarihli parti organizasyonu yöneticilerin ortak kararı ile iptal edilmiştir. Lütfen bir sonraki organizasyon için beklemede kalın."
    )
    AKTIF_PARTI_TARIHI = None
    await update.message.reply_text("✅ Parti iptal edildi.")

# --- DOSYA LİSTESİ ---
async def parti_listesi_dosya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    if not PARTI_LISTESI:
        await update.message.reply_text("📋 Liste boş.")
        return
    
    # Sıralama ve dosya oluşturma
    sirali = sorted(PARTI_LISTESI.items(), key=lambda x: x[1]['sayi'], reverse=True)
    dosya_icerik = "OYUNCU İSMİ - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in sirali])
    
    bio = io.BytesIO(dosya_icerik.encode())
    bio.name = "parti_listesi.txt"
    await update.message.reply_document(document=InputFile(bio), caption="📋 Güncel parti listesi.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CommandHandler("partibaslat", parti_baslat))
    app.add_handler(CommandHandler("partiiptal", parti_iptal))
    app.add_handler(CommandHandler("partilistesi", parti_listesi_dosya))
    app.add_handler(CommandHandler("temizle", temizle))
    
    # Mesaj kontrol (Kullanıcı etkileşimleri)
    # (Diğer yardımcı handlerlar burada kalmalı)
    
    logger.info("✅ Bot aktif!")
    app.run_polling()

if __name__ == "__main__":
    main()
