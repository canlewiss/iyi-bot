import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import io

# --- LOGGING ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- CONFIGURATION ---
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = [7924242319, 1293227694, 5656861374]
PARTI_GRUP_ID = -1003991253158
PARTI_KONU_ID = 2

# --- BOT STATE CLASS (Hata almamak için değişkenleri burada tutuyoruz) ---
class BotData:
    parti_listesi = {}
    kullanici_durumlari = {}
    aktif_tarih = None
    yasakli_kelimeler = {"küfür1", "argo1", "pislik", "aq", "lan"}

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Merhaba {update.effective_user.first_name}! Bot aktif 🚀 /menu")

async def kayit_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BotData.kullanici_durumlari[update.effective_user.id] = {"durum": "ISIM"}
    await update.message.reply_text("🎮 Oyun içi isminiz nedir?")

async def yonetici_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    kb = [[InlineKeyboardButton("🎉 Parti Kur", callback_data="kur")],
          [InlineKeyboardButton("🚫 İptal", callback_data="iptal")],
          [InlineKeyboardButton("📋 Liste", callback_data="liste")]]
    await update.message.reply_text("🛠 YÖNETİCİ PANELİ", reply_markup=InlineKeyboardMarkup(kb))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "kur":
        BotData.kullanici_durumlari[query.from_user.id] = {"durum": "TARIH"}
        await query.edit_message_text("📅 Tarihi girin:")
    
    elif query.data == "onay_kur":
        bot_url = f"https://t.me/{(await context.bot.get_me()).username}?start=kayit"
        await context.bot.send_message(PARTI_GRUP_ID, message_thread_id=PARTI_KONU_ID, 
            text=f"🎉 **{BotData.aktif_tarih}** için parti! /kayit yaz:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Kayıt Ol", url=bot_url)]]))
        await query.edit_message_text("✅ Etkinlik başlatıldı.")
    
    elif query.data == "liste":
        if not BotData.parti_listesi: await query.edit_message_text("📋 Liste boş.")
        else:
            txt = "\n".join([f"{v['isim']}: {v['sayi']} Parti" for v in BotData.parti_listesi.values()])
            bio = io.BytesIO(txt.encode()); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))
            await query.edit_message_text("✅ Liste gönderildi.")

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    
    if any(k in txt.lower() for k in BotData.yasakli_kelimeler):
        await update.message.delete()
        return

    if uid in BotData.kullanici_durumlari:
        durum = BotData.kullanici_durumlari[uid]["durum"]
        if durum == "TARIH":
            BotData.aktif_tarih = txt
            kb = [[InlineKeyboardButton("✅ Onayla", callback_data="onay_kur")]]
            await update.message.reply_text(f"📅 '{txt}' onaylıyor musun?", reply_markup=InlineKeyboardMarkup(kb))
            del BotData.kullanici_durumlari[uid]
        elif durum == "ISIM":
            BotData.kullanici_durumlari[uid] = {"durum": "SAYI", "isim": txt}
            await update.message.reply_text("🔢 Kaç parti?")
        elif durum == "SAYI" and txt.isdigit():
            BotData.parti_listesi[uid] = {"isim": BotData.kullanici_durumlari[uid]["isim"], "sayi": int(txt)}
            await update.message.reply_text("✅ Kayıt başarılı!")
            del BotData.kullanici_durumlari[uid]

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
