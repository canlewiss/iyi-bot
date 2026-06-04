import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import io

# Log ayarları
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

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
    menu = ("🛠 **Yönetici Paneli**\n\n"
            "/partibaslat - Yeni etkinlik başlat\n"
            "/partiiptal - Mevcut etkinliği iptal et\n"
            "/partilistesi - Listeyi not dosyası olarak al\n"
            "/duyuru - Gruba duyuru yap")
    await update.message.reply_text(menu, parse_mode="Markdown")

async def parti_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "TARIH_BEKLIYOR"}
    await update.message.reply_text("📅 Partinin hangi tarihte olacağını yazın (Örn: 10 Haziran 20:00):")

async def parti_iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    if not AKTIF_PARTI_TARIHI:
        await update.message.reply_text("⚠️ Şu an aktif bir parti organizasyonu yok.")
        return
    
    keyboard = [[InlineKeyboardButton("✅ Evet", callback_data="iptal_evet"), 
                 InlineKeyboardButton("❌ Hayır", callback_data="iptal_hayir")]]
    await update.message.reply_text(f"🚨 {AKTIF_PARTI_TARIHI} tarihli partiyi iptal etmek istiyor musunuz?", reply_markup=InlineKeyboardMarkup(keyboard))

# --- NOT BELGESİ OLARAK LİSTE ---
async def parti_listesi_dosya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    if not PARTI_LISTESI:
        await update.message.reply_text("📋 Liste boş.")
        return
    
    dosya_icerik = "İsim - Parti Miktarı\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for v in PARTI_LISTESI.values()])
    bio = io.BytesIO(dosya_icerik.encode())
    bio.name = "parti_listesi.txt"
    await update.message.reply_document(document=InputFile(bio), caption="📋 Güncel parti listesi ekte.")

# --- İŞLEMLER ---
async def metin_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in KULLANICI_DURUMLARI:
        durum = KULLANICI_DURUMLARI[uid]["durum"]
        if durum == "TARIH_BEKLIYOR":
            global AKTIF_PARTI_TARIHI
            AKTIF_PARTI_TARIHI = update.message.text
            keyboard = [[InlineKeyboardButton("✅ Evet", callback_data="onay_evet"), InlineKeyboardButton("❌ Hayır", callback_data="onay_hayir")]]
            await update.message.reply_text(f"📅 {AKTIF_PARTI_TARIHI} tarihinde başlatmayı onaylıyor musunuz?", reply_markup=InlineKeyboardMarkup(keyboard))
            del KULLANICI_DURUMLARI[uid]
    
    # Parti katılım mantığı (Önceki mantıkla aynı devam eder)
    # ... (Mevcut parti kayıt kodlarınız buraya eklenecek)

async def buton_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "onay_evet":
        await query.edit_message_text(f"✅ Parti {AKTIF_PARTI_TARIHI} için başlatıldı!")
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=parti"
        await context.bot.send_message(GRUP_ID, f"📢 {AKTIF_PARTI_TARIHI} için parti başladı! Katılmak için butona basın.", 
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Katıl", url=bot_url)]]))
    
    elif data == "iptal_evet":
        await context.bot.send_message(GRUP_ID, f"🚫 {AKTIF_PARTI_TARIHI} tarihli parti organizasyonu yöneticilerin kararı ile iptal edilmiştir.")
        global AKTIF_PARTI_TARIHI
        AKTIF_PARTI_TARIHI = None
        await query.edit_message_text("✅ İptal edildi.")
    # ... (Diğer buton mantıkları)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CommandHandler("partibaslat", parti_baslat))
    app.add_handler(CommandHandler("partiiptal", parti_iptal))
    app.add_handler(CommandHandler("partilistesi", parti_listesi_dosya))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, metin_kontrol))
    app.add_handler(CallbackQueryHandler(buton_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
