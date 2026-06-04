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

# DUYURU KOMUTU (Sadece Yöneticiler Grupta Kullanabilir)
async def duyuru_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER:
        return # Yönetici değilse hiçbir tepki verme

    # Komuttan sonraki mesaj kısmını al
    mesaj = update.message.text.replace("/duyuru", "").strip()

    if not mesaj:
        await update.message.reply_text("⚠️ Kullanım şekli: /duyuru [Yazmak istediğiniz mesaj]")
        return

    # Eğer komut grupta yazıldıysa orijinal mesajı sil
    if update.effective_chat.type in ["group", "supergroup"]:
        try:
            await update.message.delete()
        except Exception as e:
            logger.warning(f"Duyuru komutu silinemedi: {e}")

        # Botun ağzından duyuruyu yap
        duyuru_metni = f"📢 **DUYURU**\n\n{mesaj}"
        await context.bot.send_message(chat_id=update.message.chat_id, text=duyuru_metni, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Bu komutu duyuru yapmak istediğin grubun içine yazmalısın!")

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

# YÖNETİCİ DM SOHBET VE KÜFÜR KONTROL SİSTEMİ
async def metin_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mesaj = update.message.text
    kullanici_id = update.effective_user.id

    # 1. DURUM: EĞER MESAJ ÖZELDEN (DM) VE BİR YÖNETİCİDEN GELİYORSA (Yapay Zeka Altyapısı)
    if update.effective_chat.type == "private":
        if kullanici_id in YONETICILER:
            # Buraya ileride yapay zeka entegrasyonu gelecek
            await update.message.reply_text(f"🤖 Yönetici sistemine bağlandınız. Şu an gerçek bir yapay zeka modülüm yok, ama mesajını aldım: '{mesaj}'\n\n(Beni tam bir yapay zekaya çevirmek istersen geliştiriciye API bağlamasını söyleyebilirsin!)")
        return

    # 2. DURUM: EĞER MESAJ GRUPTAN GELİYORSA (Küfür Kontrolü)
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
    app.add_handler(CommandHandler("duyuru", duyuru_komutu)) # Yeni Duyuru Komutu
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uyeleri_karsila))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, metin_kontrol)) # Güncellenmiş Metin Dinleyici
    app.add_handler(CallbackQueryHandler(buton_tiklama_yoneticisi))

    logger.info("✅ Bot başarıyla ayağa kalktı. Duyuru sistemi ve AI altyapısı aktif...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
