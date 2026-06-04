import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Log ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# DOĞRUDAN EKLENMİŞ TOKEN
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"

# YÖNETİCİ ID LİSTESİ
YONETICILER = [7924242319, 1293227694, 5656861374]

# SUNDAY CITY GRUBUNUN ID NUMARASI
GRUP_ID = -1003991253158

# YASAKLI KELİMELER LİSTESİ
KUFURLER = ["küfür1", "küfür2", "argo1", "aptal", "salak"] 

# GRUP VE ÖZEL KARŞILAMA MESAJLARI
GRUP_MESAJLARI = [
    "🔥 Şehre yeni biri giriş yaptı! Hoş geldin {isim}, Sunday City sokakları seni bekliyor.",
    "👋 {isim} aramıza katıldı! Sunday City'de adını duyurmaya hazır mısın?",
    "🏙️ Yeni bir efsane mi doğuyor? Sunday City'nin en yeni sakini {isim}, hoş geldin!"
]
OZEL_MESAJLAR = [
    "Selam {isim}! Sunday City grubuna katıldığın için teşekkürler. Herhangi bir sorun olursa yöneticilere ulaşmaktan çekinme. İyi oyunlar! 🎮"
]

KURALLAR_METNI = """📜 **Sunday City Resmi Grup Kuralları:**
1️⃣ Saygı esastır. Küfür, hakaret ve siyaset anında ban sebebidir.
2️⃣ Spam ve reklam yasaktır.
3️⃣ Oyun içi hile satışı/paylaşımı yasaktır.
İyi oyunlar! 🎮"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Merhaba {user.first_name}! Ben Sunday City asistanıyım. Şehirde işler yolunda. 🚀")

# DUYURU KOMUTU (Sadece Özelden Çalışır ve Sabitler)
async def duyuru_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kullanici_id = update.effective_user.id
    
    if kullanici_id not in YONETICILER:
        return

    # Sadece Özel Mesajdan (DM) atılmasına izin ver
    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ Güvenlik gereği duyuruları sadece bana özelden (DM) mesaj atarak yapabilirsin!")
        try:
            await update.message.delete() # Grupta komut yazdıysa gizlemek için siler
        except Exception:
            pass
        return

    mesaj = update.message.text.replace("/duyuru", "").strip()

    if not mesaj:
        await update.message.reply_text("⚠️ Kullanım şekli: /duyuru [Yazmak istediğiniz duyuru metni]")
        return

    try:
        # 1. Aşama: Mesajı gruba gönder
        duyuru_metni = f"📢 **YÖNETİM DUYURUSU**\n\n{mesaj}"
        giden_mesaj = await context.bot.send_message(chat_id=GRUP_ID, text=duyuru_metni, parse_mode="Markdown")
        
        # 2. Aşama: Gönderilen mesajı grupta başa sabitle (Pin)
        await context.bot.pin_chat_message(chat_id=GRUP_ID, message_id=giden_mesaj.message_id)
        
        # 3. Aşama: Yöneticiye başarı mesajı dön
        await update.message.reply_text("✅ Duyuru başarıyla Sunday City grubuna gönderildi ve başa sabitlendi!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Hata oluştu! Botun grupta 'Mesaj Sabitleme' (Pin) yetkisi olduğundan emin ol. (Hata detayı: {e})")

async def yeni_uyeleri_karsila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for yeni_uye in update.message.new_chat_members:
        if yeni_uye.is_bot:
            continue
        
        isim = yeni_uye.first_name
        secilen_grup_mesaji = random.choice(GRUP_MESAJLARI).format(isim=isim)
        tam_mesaj = f"{secilen_grup_mesaji}\n\nGrup kurallarımızı okumayı unutma ☺️"
        
        klavye = [[InlineKeyboardButton("📜 Grup Kurallarımız", callback_data="kurallari_goster")]]
        reply_markup = InlineKeyboardMarkup(klavye)
        
        await update.message.reply_text(tam_mesaj, reply_markup=reply_markup)

        secilen_ozel_mesaj = random.choice(OZEL_MESAJLAR).format(isim=isim)
        try:
            await context.bot.send_message(chat_id=yeni_uye.id, text=secilen_ozel_mesaj)
        except Exception:
            pass

async def metin_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mesaj = update.message.text
    kullanici_id = update.effective_user.id

    if update.effective_chat.type == "private":
        if kullanici_id in YONETICILER:
            # DM'den duyuru komutu harici bir şey yazılırsa cevap verir
            if not mesaj.startswith("/"):
                await update.message.reply_text("🤖 Yönetici Paneli: Gruba duyuru yapmak için /duyuru [mesajınız] komutunu kullanabilirsiniz.")
        return

    mesaj_kucuk = mesaj.lower()
    chat_id = update.message.chat_id
    kullanici = update.effective_user

    for kufur in KUFURLER:
        if kufur in mesaj_kucuk:
            try:
                await update.message.delete()
            except Exception:
                pass

            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"⚠️ {kullanici.first_name}, kuralları ihlal ettin! Küfür/hakaret içerikli mesaj göndermek yasaktır. Yöneticilere bildirildi."
            )

            klavye = [
                [
                    InlineKeyboardButton("✅ Evet (Gruptan At)", callback_data=f"at_{chat_id}_{kullanici.id}"),
                    InlineKeyboardButton("❌ Hayır (Uyarı Yeterli)", callback_data="iptal_et")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(klavye)
            
            yonetici_mesaji = (
                f"🚨 **Kural İhlali Bildirimi!**\n\n"
                f"Üye: {kullanici.first_name} (@{kullanici.username if kullanici.username else 'Kullanıcı adı yok'})\n"
                f"Mesajı: {mesaj}\n\n"
                f"Bu oyuncuyu gruptan atmak ister misiniz?"
            )
            
            for yonetici in YONETICILER:
                try:
                    await context.bot.send_message(chat_id=yonetici, text=yonetici_mesaji, reply_markup=reply_markup, parse_mode="Markdown")
                except Exception:
                    pass
            break

async def buton_tiklama_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tiklayan_kisi = query.from_user
    
    await query.answer() 

    if query.data == "kurallari_goster":
        try:
            await context.bot.send_message(chat_id=tiklayan_kisi.id, text=KURALLAR_METNI)
            await query.answer(text="📜 Kurallar özel mesaj olarak sana gönderildi!", show_alert=False)
        except Exception:
            await query.answer(text="⚠️ Kuralları gönderebilmem için botun üzerine tıklayıp önce /start mesajı atmalısın!", show_alert=True)
            
    elif query.data.startswith("at_") or query.data == "iptal_et":
        if tiklayan_kisi.id not in YONETICILER:
            await query.answer(text="⚠️ Bu butonu kullanmaya yetkiniz yok!", show_alert=True)
            return

        if query.data.startswith("at_"):
            veri = query.data.split("_")
            grup_id = int(veri[1])
            atilan_kisi_id = int(veri[2])
            
            try:
                await context.bot.ban_chat_member(chat_id=grup_id, user_id=atilan_kisi_id)
                await query.edit_message_text(text=f"{query.message.text}\n\n✅ **İşlem Başarılı:** Oyuncu {tiklayan_kisi.first_name} tarafından gruptan atıldı!", parse_mode="Markdown")
            except Exception:
                await query.edit_message_text(text=f"{query.message.text}\n\n⚠️ **Hata:** Oyuncu atılamadı. Botun grupta yetkilerini kontrol edin.", parse_mode="Markdown")
                
        elif query.data == "iptal_et":
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **İşlem İptal Edildi:** {tiklayan_kisi.first_name} sadece uyarı verilmesini seçti.", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru_komutu))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uyeleri_karsila))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, metin_kontrol))
    app.add_handler(CallbackQueryHandler(buton_tiklama_yoneticisi))

    logger.info("✅ Bot başarıyla ayağa kalktı. DM duyuru ve pinleme sistemi aktif...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
