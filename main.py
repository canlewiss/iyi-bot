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

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcı adını al ve kişisel karşıla
    user_name = update.effective_user.first_name
    
    # Hem /start hem de /kayıt için ortak kayıt akışını tetikle
    if (update.message.text and "/kayit" in update.message.text.lower()) or (context.args and context.args[0] == "kayit"):
        KULLANICI_DURUMLARI[update.effective_user.id] = {"durum": "ISIM_BEKLIYOR"}
        await update.message.reply_text(f"🎮 Merhaba {user_name}! Kayıt ekranına hoş geldin. Lütfen oyun içi ismini yaz:")
    else:
        await update.message.reply_text(f"Merhaba {user_name}! Bot başarıyla çalışıyor 🚀 /menu")

async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER:
        await update.message.reply_text("⚠️ Bu komut sadece yöneticilere özeldir.")
        return
    keyboard = [
        [InlineKeyboardButton("🎉 Parti Başlat", callback_data="admin_baslat")],
        [InlineKeyboardButton("🚫 Parti İptal", callback_data="admin_iptal")],
        [InlineKeyboardButton("📋 Listeyi Al", callback_data="admin_liste")],
        [InlineKeyboardButton("🧹 Temizle", callback_data="admin_temizle")]
    ]
    await update.message.reply_text("🛠 **YÖNETİCİ PANELİ**", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    if uid not in YONETICILER: return

    if query.data == "admin_baslat":
        KULLANICI_DURUMLARI[uid] = {"durum": "TARIH_BEKLIYOR"}
        await query.edit_message_text("📅 Partinin tarihini girin:")
    
    elif query.data == "onay_baslat":
        global AKTIF_PARTI_TARIHI
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=kayit"
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🎉 **{AKTIF_PARTI_TARIHI} Parti Etkinliği Başlıyor!**\n👇 Kayıt olmak için /kayit yaz veya butona tıkla!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Kayıt Ol", url=bot_url)]]))
        await query.edit_message_text("✅ Etkinlik başlatıldı.")

    elif query.data == "admin_iptal":
        keyboard = [[InlineKeyboardButton("✅ Evet", callback_data="onay_iptal"), InlineKeyboardButton("❌ Hayır", callback_data="iptal_vazgec")]]
        await query.edit_message_text("🚨 Partiyi iptal etmek istiyor musunuz?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "onay_iptal":
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, text="🚫 Parti organizasyonu iptal edilmiştir.")
        await query.edit_message_text("✅ İptal edildi.")

    elif query.data == "admin_liste":
        if not PARTI_LISTESI: await query.edit_message_text("📋 Liste boş.")
        else:
            txt = "İSİM - PARTİ MİKTARI\n" + "\n".join([f"{v['isim']} - {v['sayi']}" for k, v in PARTI_LISTESI.items()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))
            await query.edit_message_text("✅ Liste gönderildi.")
    
    elif query.data == "iptal_vazgec":
        await query.edit_message_text("❌ İşlem iptal edildi.")

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid = update.effective_user.id
    text = update.message.text

    if any(k in text.lower() for k in YASAKLI_KELIMELER):
        await update.message.delete()
        return

    if uid in KULLANICI_DURUMLARI and KULLANICI_DURUMLARI[uid].get("durum") == "TARIH_BEKLIYOR":
        global AKTIF_PARTI_TARIHI
        AKTIF_PARTI_TARIHI = text
        keyboard = [[InlineKeyboardButton("✅ Evet", callback_data="onay_baslat"), InlineKeyboardButton("❌ Hayır", callback_data="iptal_vazgec")]]
        await update.message.reply_text(f"📅 '{text}' onaylıyor musunuz?", reply_markup=InlineKeyboardMarkup(keyboard))
        del KULLANICI_DURUMLARI[uid]
        return

    if uid in KULLANICI_DURUMLARI and KULLANICI_DURUMLARI[uid].get("durum") == "ISIM_BEKLIYOR":
        KULLANICI_DURUMLARI[uid] = {"durum": "SAYI_BEKLIYOR", "isim": text}
        await update.message.reply_text("🔢 Kaç parti vereceksiniz?")
    elif uid in KULLANICI_DURUMLARI and KULLANICI_DURUMLARI[uid].get("durum") == "SAYI_BEKLIYOR" and text.isdigit():
        PARTI_LISTESI[uid] = {"isim": KULLANICI_DURUMLARI[uid]["isim"], "sayi": int(text)}
        await update.message.reply_text("✅ Kayıt başarılı!")
        del KULLANICI_DURUMLARI[uid]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", start)) # Yeni komut eklendi
    app.add_handler(CommandHandler("menu", yonetici_menu))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT, mesaj_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
