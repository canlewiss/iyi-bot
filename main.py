```python
import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters
)

# --- AYARLAR ---
# Token ve ID bilgilerini buraya sabitliyoruz
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
YONETICILER = {7924242319, 1293227694, 5656861374}
PARTI_GRUP_ID = -1003991253158

logging.basicConfig(level=logging.INFO)

# --- VERİ VE DURUM YÖNETİCİSİ ---
class BotManager:
    def __init__(self):
        self.parti_listesi = {}
        self.kullanici_durumlari = {} # uid -> {"durum": "...", "isim": "..."}
        self.aktif_tarih = None
        self.yasakli_kelimeler = {"aq", "amk", "oç", "piç", "lan"}

    def temizle(self):
        self.parti_listesi = {}
        self.aktif_tarih = None

# Global manager nesnesi (Sınıf tabanlı olduğu için global hatası vermez)
manager = BotManager()

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Sunday City Bot aktif! Kayıt için /kayit yazın.")

async def kayit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager.kullanici_durumlari[update.effective_user.id] = {"durum": "ISIM_BEKLIYOR"}
    await update.message.reply_text("🎮 Kayıt için oyun içi isminizi yazar mısınız?")

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER: return
    kb = [
        [InlineKeyboardButton("🎉 Parti Kur", callback_data="kur")],
        [InlineKeyboardButton("📋 Listeyi Al", callback_data="liste")],
        [InlineKeyboardButton("🚫 Sıfırla", callback_data="reset")]
    ]
    await update.message.reply_text("🛠 Admin Paneli", reply_markup=InlineKeyboardMarkup(kb))

# --- İŞLEMCİLER ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "kur":
        manager.kullanici_durumlari[query.from_user.id] = {"durum": "TARIH_BEKLIYOR"}
        await query.edit_message_text("📅 Partinin tarihini girin:")
    elif query.data == "liste":
        if not manager.parti_listesi: await query.edit_message_text("📋 Liste boş.")
        else:
            txt = "\n".join([f"{v['isim']}: {v['sayi']} Parti" for v in manager.parti_listesi.values()])
            bio = io.BytesIO(txt.encode('utf-8')); bio.name = "liste.txt"
            await query.message.reply_document(document=InputFile(bio))
    elif query.data == "reset":
        manager.temizle()
        await query.edit_message_text("✅ Sistem sıfırlandı.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    txt = update.message.text
    
    # Küfür Kontrolü
    if any(k in txt.lower() for k in manager.yasakli_kelimeler):
        await update.message.delete()
        return

    # Durum Yönetimi
    if uid in manager.kullanici_durumlari:
        durum = manager.kullanici_durumlari[uid]
        
        if isinstance(durum, dict) and durum.get("durum") == "TARIH_BEKLIYOR":
            manager.aktif_tarih = txt
            await update.message.reply_text(f"✅ Parti tarihi '{txt}' olarak ayarlandı.")
            del manager.kullanici_durumlari[uid]
            
        elif durum == "ISIM_BEKLIYOR":
            manager.kullanici_durumlari[uid] = {"durum": "SAYI_BEKLIYOR", "isim": txt}
            await update.message.reply_text("🔢 İsim alındı. Kaç parti vereceksin?")
            
        elif isinstance(durum, dict) and durum.get("durum") == "SAYI_BEKLIYOR":
            if txt.isdigit():
                manager.parti_listesi[uid] = {"isim": durum["isim"], "sayi": txt}
                await update.message.reply_text("✅ Kayıt başarılı!")
                del manager.kullanici_durumlari[uid]
            else:
                await update.message.reply_text("⚠️ Lütfen geçerli bir sayı girin.")

# --- ANA DÖNGÜ ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", kayit))
    app.add_handler(CommandHandler("menu", admin_menu))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot sorunsuz başlatıldı!")
    app.run_polling()

```
