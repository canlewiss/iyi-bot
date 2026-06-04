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

# Veri Depoları
PARTI_LISTESI = {}
KULLANICI_DURUMLARI = {}
AKTIF_PARTI_TARIHI = None
YASAKLI_KELIMELER = ["küfür1", "argo1", "pislik", "aq", "lan"]

# --- YÖNETİCİ PANELİ BUTONLARI ---
async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    keyboard = [
        [InlineKeyboardButton("🎉 Parti Kur", callback_data="admin_baslat")],
        [InlineKeyboardButton("🚫 Parti İptal", callback_data="admin_iptal")],
        [InlineKeyboardButton("📋 Listeyi Al", callback_data="admin_liste")]
    ]
    await update.message.reply_text("🛠 **YÖNETİCİ KONTROL PANELİ**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- BUTON VE ONAY İŞLEMLERİ ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    if uid not in YONETICILER: return

    # 1. Parti Başlatma Akışı (Onaylı)
    if query.data == "admin_baslat":
        await query.edit_message_text("📅 Lütfen partinin tarihini yazın (Örn: 10 Haziran 20:00):")
        KULLANICI_DURUMLARI[uid] = {"durum": "TARIH_BEKLIYOR"}

    elif query.data == "onay_baslat":
        global AKTIF_PARTI_TARIHI
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=kayit"
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🎉 **{AKTIF_PARTI_TARIHI} Parti Etkinliği Başlıyor!**\n👇 Kayıt için butona tıkla!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Kayıt Ol", url=bot_url)]]))
        await query.edit_message_text("✅ Etkinlik başarıyla başlatıldı.")

    # 2. Parti İptal Akışı (Onaylı)
    elif query.data == "admin_iptal":
        if not AKTIF_PARTI_TARIHI:
            await query.edit_message_text("⚠️ Aktif parti yok.")
            return
        keyboard = [[InlineKeyboardButton("✅ Evet", callback_data="onay_iptal"), InlineKeyboardButton("❌ Hayır", callback_data="admin_iptal_iptal")]]
        await query.edit_message_text(f"🚨 {AKTIF_PARTI_TARIHI} tarihli partiyi iptal etmek istiyor musunuz?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "onay_iptal":
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, text=f"🚫 {AKTIF_PARTI_TARIHI} tarihli parti organizasyonu yöneticilerin ortak kararı ile iptal edilmiştir.")
        AKTIF_PARTI_TARIHI = None
        await query.edit_message_text("✅ Parti iptal edildi.")

    # --- Diğer Paneller ---
    elif query.data == "admin_liste":
        if not PARTI_LISTESI: await query.edit_message_text("📋 Liste boş.")
        else:
            txt = "İSİM - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in PARTI_LISTESI.items()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))
            await query.edit_message_text("✅ Liste gönderildi.")

    elif query.data == "admin_iptal_iptal":
        await query.edit_message_text("❌ İşlem iptal edildi.")

# --- MESAJ İŞLEME ---
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid = update.effective_user.id
    text = update.message.text

    # Küfür
    if any(k in text.lower() for k in YASAKLI_KELIMELER):
        await update.message.delete()
        return

    # Tarih Girme Aşaması
    if uid in KULLANICI_DURUMLARI and KULLANICI_DURUMLARI[uid].get("durum") == "TARIH_BEKLIYOR":
        global AKTIF_PARTI_TARIHI
        AKTIF_PARTI_TARIHI = text
        keyboard = [[InlineKeyboardButton("✅ Evet Başlat", callback_data="onay_baslat"), InlineKeyboardButton("❌ Hayır", callback_data="admin
