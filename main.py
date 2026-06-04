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

# ⚠️ BURAYA KENDİ TELEGRAM ID NUMARANI YAZMALISIN ⚠️
# @userinfobot isimli bota start vererek kendi ID'ni öğrenebilirsin.
YONETICI_ID = 123456789 

# YASAKLI KELİMELER LİSTESİ (Burayı dilediğin gibi çoğaltabilirsin)
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

# YENİ ÖZELLİK: Küfür ve Hakaret Kontrol Sistemi
async def kufur_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Eğer mesaj metni yoksa (fotoğraf vb. ise) işlem yapma
    if not update.message or not update.message.text:
        return

    mesaj = update.message.text.lower()
    kullanici = update.effective_user
    chat_id = update.message.chat_id

    # Yöneticileri kontrol etmeme özelliği eklenebilir ama şimdilik herkesi denetliyor
    for kufur in KUFURLER:
        # Eğer mesajın içinde yasaklı kelime varsa
        if kufur in mesaj:
            # 1. Kötü mesajı gruptan sil
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Mesaj silinemedi (Botun mesaj silme yetkisi olmayabilir): {e}")

            # 2. Oyuncuyu grupta etiketleyerek uyar
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"⚠️ {kullanici.first_name}, kuralları ihlal ettin! Küfür/hakaret içerikli mesaj göndermek yasaktır. Yöneticilere bildirildi."
            )

            # 3. Yöneticiye (Sana) onay butonlu özel mesaj gönder
            klavye = [
                [
                    # at_GrupID_KullaniciID şeklinde data gönderiyoruz ki bot kimi nereden atacağını bilsin
                    InlineKeyboardButton("✅ Evet (Gruptan At)", callback_data=f"at_{chat_id}_{kullanici.id}"),
                    InlineKeyboardButton("❌ Hayır (Uyarı Yeterli)", callback_data="iptal_et")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(klavye)
            
            yonetici_mesaji = (
                f"🚨 **Kural İhlali Bildirimi!**\n\n"
                f"Üye: {kullanici.first_name} (@{kullanici.username if kullanici.username else 'Kullanıcı adı yok'})\n"
                f"Mesajı: {update.message.text}\n\n"
                f"Bu oyuncuyu gruptan atmak ister misiniz?"
            )
            
            try:
                await context.bot.send_message(chat_id=YONETICI_ID, text=yonetici_mesaji, reply_markup=reply_markup, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Yöneticiye mesaj atılamadı. Yönetici bota DM'den /start dememiş olabilir: {e}")
            
            # Küfür bulunduysa diğer kelimeleri aramaya gerek yok, döngüyü kır
            break

async def buton_tiklama_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tiklayan_kisi = query.from_user
    
    await query.answer() 

    # Grup Kuralları Butonu
    if query.data == "kurallari_goster":
        try:
            await context.bot.send_message(chat_id=tiklayan_kisi.id, text=KURALLAR_METNI)
            await query.answer(text="📜 Kurallar özel mesaj olarak sana gönderildi!", show_alert=False)
        except Exception:
            await query.answer(text="⚠️ Kuralları gönderebilmem için botun üzerine tıklayıp önce /start mesajı atmalısın!", show_alert=True)
            
    # Gruptan At (Kick/Ban) Butonu
    elif query.data.startswith("at_"):
        # Gelen veriyi parçalayıp grup ve kullanıcı ID'sini alıyoruz
        veri = query.data.split("_")
        grup_id = int(veri[1])
        atilan_kisi_id = int(veri[2])
        
        try:
            # Kullanıcıyı gruptan at (ban)
            await context.bot.ban_chat_member(chat_id=grup_id, user_id=atilan_kisi_id)
            # Yöneticinin ekranındaki mesajı güncelle (butonları kaldır)
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ **İşlem Başarılı:** Oyuncu gruptan atıldı!", parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n⚠️ **Hata:** Oyuncu atılamadı. Botun grupta 'Kullanıcıları Engelle' yetkisi olduğundan emin ol.", parse_mode="Markdown")
            
    # Hayır (İptal) Butonu
    elif query.data == "iptal_et":
        # Yöneticinin ekranındaki mesajı güncelle (butonları kaldır)
        await query.edit_message_text(text=f"{query.message.text}\n\n❌ **İşlem İptal Edildi:** Oyuncuya sadece uyarı verildi, grupta kaldı.", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uyeleri_karsila))
    
    # KÜFÜR KONTROLÜNÜ DİNLEYEN SİSTEM (Yazı içeren tüm mesajları kontrol eder)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kufur_kontrol))
    
    app.add_handler(CallbackQueryHandler(buton_tiklama_yoneticisi))

    logger.info("✅ Bot başarıyla ayağa kalktı. Küfür filtresi ve Moderasyon aktif...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
