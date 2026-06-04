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

# Pazar Şehri evrenine uygun GRUP Karşılama Mesajları
GRUP_MESAJLARI = [
    "🔥 Şehre yeni biri giriş yaptı! Hoş geldin {isim}, Sunday City sokakları seni bekliyor.",
    "👋 {isim} aramıza katıldı! Sunday City'de adını duyurmaya hazır mısın?",
    "🏙️ Yeni bir efsane mi doğuyor? Sunday City'nin en yeni sakini {isim}, hoş geldin!",
    "🚨 Dikkat! {isim} şehre adım attı. Pazar Şehri kurallarına uymayı unutma!",
    "😎 Sunday City ailesi büyüyor! Mekanın yeni sahibi {isim} hoş geldin."
]

# Pazar Şehri evrenine uygun ÖZEL (DM) Karşılama Mesajları
OZEL_MESAJLAR = [
    "Selam {isim}! Sunday City grubuna katıldığın için teşekkürler. Herhangi bir sorun olursa yöneticilere ulaşmaktan çekinme. İyi oyunlar! 🎮",
    "Hoş geldin {isim}! Burası Sunday City arka planı. Şehirde hayatta kalmak için gruptaki sabitlenmiş kuralları okumayı unutma! 📜",
    "Sunday City'nin kalbine, resmi grubumuza hoş geldin {isim}! Oyunla ilgili taktiklere ihtiyacın olursa grupta sormaktan çekinme. 🚀"
]

# BUTONA TIKLANDIĞINDA GÖRÜNECEK DETAYLI KURALLAR METNİ
KURALLAR_METNI = """📜 **Sunday City Resmi Grup Kuralları:**

Şehrimizin huzuru ve oyun deneyimimizin kalitesi için aşağıdaki kurallara uymak zorunludur:

1️⃣ **Saygı ve Üslup:** Grup içerisinde küfür, argo, hakaret ve aşağılayıcı kelimeler kullanmak kesinlikle yasaktır. Din, dil, ırk ayrımı yapmak ve siyasi tartışmalara girmek anında uzaklaştırma (ban) sebebidir.

2️⃣ **Spam ve Reklam:** Başka Telegram gruplarının, Discord sunucularının veya farklı oyunların reklamını yapmak, referans (davet) linkleri paylaşmak yasaktır. Sohbet akışını bozacak şekilde art arda mesaj (flood) atmaktan, anlamsız GIF veya çıkartma spamı yapmaktan kaçının.

3️⃣ **Oyun İçi Hile ve Ticaret:** Oyunda haksız avantaj sağlayan 3. parti yazılım (hile, modlu APK, makro vb.) paylaşımı veya teşviki yasaktır. Gerçek parayla (TL, Kripto vb.) hesap alım-satımı veya takası grupta yasaktır; olası dolandırıcılık durumlarında yönetim sorumluluk kabul etmez.

4️⃣ **Kişisel Gizlilik:** Kendi güvenliğiniz veya başkalarının güvenliği için telefon numarası, adres, şifre gibi kişisel bilgilerinizi grupta kesinlikle paylaşmayın.

5️⃣ **Yardımlaşma:** Oyuna yeni başlayanlara karşı sabırlı ve yardımsever olun. Şehre yeni adım atmış oyunculara Sunday City'de hayatta kalma taktikleri vererek topluluğumuzu güçlendirin.

6️⃣ **Yönetim Kararları:** Grup yöneticileri (Adminler) kuralları uygulama ve kural ihlali durumunda uyarı yapmadan gruptan çıkarma hakkına sahiptir. Yönetim kararlarıyla ilgili şikayetlerinizi grupta tartışmak yerine yöneticilere özel mesaj (DM) yoluyla iletebilirsiniz.

Şehre katkı sağladığın için teşekkürler! İyi oyunlar dileriz! 🎮🏙️"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Merhaba {user.first_name}! Ben Sunday City asistanıyım. Şehirde işler yolunda. 🚀")

async def yeni_uyeleri_karsila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for yeni_uye in update.message.new_chat_members:
        # Botların gruba katılmasını yoksay
        if yeni_uye.is_bot:
            continue
        
        isim = yeni_uye.first_name

        # 1. Aşama: Rastgele mesajı seç ve "kuralları okumayı unutma" ekini yapıştır
        secilen_grup_mesaji = random.choice(GRUP_MESAJLARI).format(isim=isim)
        tam_mesaj = f"{secilen_grup_mesaji}\n\nGrup kurallarımızı okumayı unutma ☺️"

        # 2. Aşama: Butonu Oluştur
        klavye = [
            [InlineKeyboardButton("📜 Grup Kurallarımız", callback_data="kurallari_goster")]
        ]
        reply_markup = InlineKeyboardMarkup(klavye)

        # 3. Aşama: Mesajı butonla birlikte gruba gönder
        await update.message.reply_text(tam_mesaj, reply_markup=reply_markup)

        # 4. Aşama: Kişiye özelden mesaj gönder (Önceki güvenli sistem)
        secilen_ozel_mesaj = random.choice(OZEL_MESAJLAR).format(isim=isim)
        try:
            await context.bot.send_message(chat_id=yeni_uye.id, text=secilen_ozel_mesaj)
            logger.info(f"{isim} adlı kişiye özel mesaj gönderildi.")
        except Exception as e:
            logger.warning(f"{isim} adlı kişiye özel mesaj gönderilemedi (Bota start vermemiş olabilir).")

# Butona tıklandığında çalışacak olan fonksiyon
async def buton_tiklama_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Telegram'a "Tıklamayı algıladım, yükleniyor ikonunu durdur" diyoruz
    await query.answer() 

    # Eğer tıklanan butonun verisi (callback_data) "kurallari_goster" ise:
    if query.data == "kurallari_goster":
        # Kurallar metnini gruba gönder
        await query.message.reply_text(KURALLAR_METNI)

def main():
    app = Application.builder().token(TOKEN).build()

    # Komut ve Dinleyiciler (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uyeleri_karsila))
    
    # Buton tıklamalarını dinleyecek eklenti
    app.add_handler(CallbackQueryHandler(buton_tiklama_yoneticisi))

    logger.info("✅ Bot başarıyla ayağa kalktı, butonlar ve detaylı kurallar aktif...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
