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

# SUNDAY CITY ANA GRUBUNUN ID NUMARASI
GRUP_ID = -1003991253158

# YASAKLI KELİMELER LİSTESİ
KUFURLER = ["küfür1", "küfür2", "argo1", "aptal", "salak"] 

# PARTİ SİSTEMİ İÇİN VERİTABANI (Hafıza)
PARTI_LISTESI = {}        
KULLANICI_DURUMLARI = {}  

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

PARTI_KURALLARI = """📜 **Parti Etkinliği Kuralları:**
1️⃣ Parti zamanında oyunda ve aktif olunmalıdır.
2️⃣ Söz verdiğiniz parti miktarını eksiksiz teslim etmelisiniz.
3️⃣ Sırayı bozmak veya başkasının hakkını yemek yasaktır."""

def liste_olustur():
    if not PARTI_LISTESI:
        return "📋 Şu an parti listesi tamamen boş.", []
        
    # Listeyi en çok parti verenden en aza doğru sıralar
    sirali_liste = sorted(PARTI_LISTESI.items(), key=lambda item: item[1]['sayi'], reverse=True)
    
    metin = "📋 **GÜNCEL PARTİ LİSTESİ**\n\n"
    klavye = []
    
    sayac = 1
    toplam_parti = 0
    
    for uid, veri in sirali_liste:
        metin += f"*{sayac}.* {veri['isim']} - {veri['sayi']} Parti\n"
        toplam_parti += veri['sayi']
        klavye.append([InlineKeyboardButton(f"❌ {veri['isim']} adlı oyuncuyu sil", callback_data=f"psil_{uid}")])
        sayac += 1
        
    metin += f"\n📊 **Toplam Parti Miktarı:** {toplam_parti}"
    return metin, klavye

# GÜNCELLENEN KISIM: Deep Link (Buton Yönlendirmesi) Özellikli Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_id = user.id

    # Eğer oyuncu butona tıklayarak bota geldiyse Telegram arka planda "/start parti" komutunu gönderir
    if context.args and context.args[0] == "parti":
        if kullanici_id in PARTI_LISTESI:
            klavye = [
                [InlineKeyboardButton("✅ Evet (Listeden Çık)", callback_data=f"cikis_evet_{kullanici_id}"),
                 InlineKeyboardButton("❌ Hayır (Listede Kal)", callback_data=f"cikis_hayir_{kullanici_id}")]
            ]
            await update.message.reply_text(
                f"⚠️ {user.first_name}, zaten parti etkinliğine katıldınız. Çıkmak istiyor musunuz?",
                reply_markup=InlineKeyboardMarkup(klavye)
            )
        else:
            klavye = [
                [InlineKeyboardButton("✅ Evet", callback_data=f"parti_evet_{kullanici_id}"),
                 InlineKeyboardButton("❌ Hayır", callback_data=f"parti_hayir_{kullanici_id}")]
            ]
            await update.message.reply_text(
                f"🎉 Merhaba {user.first_name}! Parti etkinliğine katılmak ister misin?\n(Kayıt işlemi burada, kimseden habersiz gizlice yapılacaktır.)",
                reply_markup=InlineKeyboardMarkup(klavye)
            )
        return

    # Normal bir şekilde bota girip başlatanlar için
    await update.message.reply_text(f"Merhaba {user.first_name}! Ben Sunday City asistanıyım. Şehirde işler yolunda. 🚀")

# YENİ KOMUT: Yöneticilerin Grupta Sabit Kayıt Butonu Oluşturması
async def parti_kur_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER:
        return
        
    try:
        await update.message.delete() # Yöneticinin yazdığı komutu silerek gizle
    except Exception:
        pass

    bot_username = (await context.bot.get_me()).username
    url = f"https://t.me/{bot_username}?start=parti"
    
    mesaj = (
        "🎉 **SUNDAY CITY PARTİ ETKİNLİĞİ BAŞLIYOR!**\n\n"
        "Etkinliğe katılıp parti vermek isteyen oyuncularımız, aşağıdaki butona tıklayarak "
        "gizli ve güvenli bir şekilde kaydını oluşturabilir.\n\n"
        "👇 *Hemen kayıt olmak için butona tıkla!*"
    )
    
    klavye = [[InlineKeyboardButton("🎉 Parti Kaydını Başlat", url=url)]]
    
    try:
        giden_mesaj = await context.bot.send_message(
            chat_id=update.message.chat_id, 
            text=mesaj, 
            reply_markup=InlineKeyboardMarkup(klavye), 
            parse_mode="Markdown"
        )
        # Mesajı gruba/odaya sabitle
        await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=giden_mesaj.message_id)
    except Exception as e:
        logger.error(f"Parti kurulamadı: {e}")

async def duyuru_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kullanici_id = update.effective_user.id
    if kullanici_id not in YONETICILER:
        return

    if update.effective_chat.type != "private":
        await update.message.reply_text("⚠️ Güvenlik gereği duyuruları sadece bana özelden (DM) mesaj atarak yapabilirsin!")
        try:
            await update.message.delete()
        except Exception:
            pass
        return

    mesaj = update.message.text.replace("/duyuru", "").strip()
    if not mesaj:
        await update.message.reply_text("⚠️ Kullanım şekli: /duyuru [Yazmak istediğiniz duyuru metni]")
        return

    try:
        duyuru_metni = f"📢 **YÖNETİM DUYURUSU**\n\n{mesaj}"
        giden_mesaj = await context.bot.send_message(chat_id=GRUP_ID, text=duyuru_metni, parse_mode="Markdown")
        await context.bot.pin_chat_message(chat_id=GRUP_ID, message_id=giden_mesaj.message_id)
        await update.message.reply_text("✅ Duyuru başarıyla Sunday City grubuna gönderildi ve başa sabitlendi!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Hata oluştu! Botun grupta 'Mesaj Sabitleme' yetkisi olduğundan emin ol.")

async def parti_listesi_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in YONETICILER:
        return 

    metin, klavye = liste_olustur()
    await update.message.reply_text(metin, reply_markup=InlineKeyboardMarkup(klavye) if klavye else None, parse_mode="Markdown")

async def yeni_uyeleri_karsila(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for yeni_uye in update.message.new_chat_members:
        if yeni_uye.is_bot:
            continue
        isim = yeni_uye.first_name
        secilen_grup_mesaji = random.choice(GRUP_MESAJLARI).format(isim=isim)
        tam_mesaj = f"{secilen_grup_mesaji}\n\nGrup kurallarımızı okumayı unutma ☺️"
        klavye = [[InlineKeyboardButton("📜 Grup Kurallarımız", callback_data="kurallari_goster")]]
        
        await update.message.reply_text(tam_mesaj, reply_markup=InlineKeyboardMarkup(klavye))
        secilen_ozel_mesaj = random.choice(OZEL_MESAJLAR).format(isim=isim)
        try:
            await context.bot.send_message(chat_id=yeni_uye.id, text=secilen_ozel_mesaj)
        except Exception:
            pass

async def metin_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mesaj = update.message.text
    mesaj_kucuk = mesaj.lower().strip()
    kullanici_id = update.effective_user.id
    kullanici = update.effective_user
    chat_id = update.message.chat_id
    konu_id = update.message.message_thread_id

    # GÜNCELLENEN KISIM: Özel Mesajda (DM) Kayıt İşlemlerini Yakalama
    if update.effective_chat.type == "private":
        if kullanici_id in KULLANICI_DURUMLARI:
            durum = KULLANICI_DURUMLARI[kullanici_id].get("durum")
            
            if durum == "ISIM_BEKLIYOR":
                KULLANICI_DURUMLARI[kullanici_id]["isim"] = mesaj
                KULLANICI_DURUMLARI[kullanici_id]["durum"] = "SAYI_BEKLIYOR"
                
                soru = f"{PARTI_KURALLARI}\n\n❓ **Peki, kaç parti vereceksiniz?** (Lütfen sadece sayıyı yazın)"
                await update.message.reply_text(soru, parse_mode="Markdown")
                return
                
            elif durum == "SAYI_BEKLIYOR":
                if not mesaj.isdigit():
                    await update.message.reply_text("⚠️ Lütfen sadece rakam kullanarak geçerli bir sayı girin (Örn: 5):")
                    return

                isim = KULLANICI_DURUMLARI[kullanici_id]["isim"]
                sayi = int(mesaj) 
                
                PARTI_LISTESI[kullanici_id] = {"isim": isim, "sayi": sayi}
                del KULLANICI_DURUMLARI[kullanici_id]
                
                sonuc_mesaji = f"✅ **İşlem Tamamlandı!**\n\nListeye başarıyla eklendin.\n👤 **Oyuncu İsmi:** {isim}\n🎁 **Vereceği Parti:** {sayi}\n\n*Etkinlik saatinde görüşmek üzere!*"
                await update.message.reply_text(sonuc_mesaji, parse_mode="Markdown")
                return

        if kullanici_id in YONETICILER and not mesaj.startswith("/"):
            await update.message.reply_text("🤖 Yönetici Paneli: Gruba duyuru yapmak için /duyuru [mesaj], parti listesini görmek için /partilistesi komutunu kullanabilirsiniz.")
        return

    # Sadece Gruptaki Mesajlarda Küfür Kontrolü Yap
    for kufur in KUFURLER:
        if kufur in mesaj_kucuk:
            try:
                await update.message.delete()
            except Exception:
                pass

            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ {kullanici.first_name}, kuralları ihlal ettin! Yöneticilere bildirildi.", message_thread_id=konu_id)
            klavye = [
                [
                    InlineKeyboardButton("✅ Evet (Gruptan At)", callback_data=f"at_{chat_id}_{kullanici_id}"),
                    InlineKeyboardButton("❌ Hayır (Uyarı Yeterli)", callback_data="iptal_et")
                ]
            ]
            yonetici_mesaji = f"🚨 **Kural İhlali!**\n\nÜye: {kullanici.first_name}\nMesajı: {mesaj}\n\nBu oyuncuyu gruptan atmak ister misiniz?"
            for yonetici in YONETICILER:
                try:
                    await context.bot.send_message(chat_id=yonetici, text=yonetici_mesaji, reply_markup=InlineKeyboardMarkup(klavye), parse_mode="Markdown")
                except Exception:
                    pass
            return 

async def buton_tiklama_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tiklayan_kisi = query.from_user
    await query.answer() 

    if query.data.startswith("parti_") or query.data.startswith("cikis_"):
        parcalar = query.data.split("_")
        hedef_id = int(parcalar[-1])
        islem = "_".join(parcalar[:-1])

        if tiklayan_kisi.id != hedef_id:
            await query.answer("⚠️ Bu buton senin için değil!", show_alert=True)
            return

        if islem == "cikis_evet":
            if tiklayan_kisi.id in PARTI_LISTESI:
                del PARTI_LISTESI[tiklayan_kisi.id]
                await query.edit_message_text("✅ Listeden başarıyla çıktınız. Dilerseniz tekrar 'PARTİ' yazarak veya butona basarak katılabilirsiniz.")
            else:
                await query.edit_message_text("⚠️ Zaten listede değilsiniz.")

        elif islem == "cikis_hayir":
            await query.edit_message_text("✅ Hayır olarak işaretlediniz, listede olmaya devam edeceksiniz.")

        elif islem == "parti_hayir":
            await query.edit_message_text("Tamamdır, partiye dahil edilmediniz. 😔")
            if tiklayan_kisi.id in KULLANICI_DURUMLARI:
                del KULLANICI_DURUMLARI[tiklayan_kisi.id]
                
        elif islem == "parti_evet":
            KULLANICI_DURUMLARI[tiklayan_kisi.id] = {"durum": "ISIM_BEKLIYOR"}
            await query.edit_message_text("Harika! 🎮 Lütfen oyundaki ismini yaz:")
        
        return 

    elif query.data.startswith("psil_"):
        if tiklayan_kisi.id not in YONETICILER:
            await query.answer("⚠️ Yetkiniz yok!", show_alert=True)
            return
            
        silinecek_id = int(query.data.split("_")[1])
        if silinecek_id in PARTI_LISTESI:
            silinen_isim = PARTI_LISTESI[silinecek_id]["isim"]
            del PARTI_LISTESI[silinecek_id]
            await query.answer(f"✅ {silinen_isim} listeden başarıyla çıkarıldı!", show_alert=False)
        
        metin, klavye = liste_olustur()
        try:
            await query.edit_message_text(text=metin, reply_markup=InlineKeyboardMarkup(klavye) if klavye else None, parse_mode="Markdown")
        except Exception:
            pass

    elif query.data == "kurallari_goster":
        try:
            await context.bot.send_message(chat_id=tiklayan_kisi.id, text=KURALLAR_METNI)
            await query.answer("📜 Kurallar özel mesaj olarak sana gönderildi!", show_alert=False)
        except Exception:
            await query.answer("⚠️ Kuralları gönderebilmem için botun üzerine tıklayıp önce /start mesajı atmalısın!", show_alert=True)
            
    elif query.data.startswith("at_") or query.data == "iptal_et":
        if tiklayan_kisi.id not in YONETICILER:
            await query.answer("⚠️ Bu butonu kullanmaya yetkiniz yok!", show_alert=True)
            return

        if query.data.startswith("at_"):
            veri = query.data.split("_")
            grup_id = int(veri[1])
            atilan_kisi_id = int(veri[2])
            try:
                await context.bot.ban_chat_member(chat_id=grup_id, user_id=atilan_kisi_id)
                await query.edit_message_text(text=f"{query.message.text}\n\n✅ **İşlem Başarılı:** Oyuncu gruptan atıldı!", parse_mode="Markdown")
            except Exception:
                await query.edit_message_text(text=f"{query.message.text}\n\n⚠️ **Hata:** Oyuncu atılamadı.", parse_mode="Markdown")
        elif query.data == "iptal_et":
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **İşlem İptal Edildi:** Sadece uyarı verildi.", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru_komutu))
    app.add_handler(CommandHandler("partilistesi", parti_listesi_komutu)) 
    app.add_handler(CommandHandler("partikur", parti_kur_komutu)) # YENİ KOMUT AKTİF EDİLDİ
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uyeleri_karsila))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, metin_kontrol))
    app.add_handler(CallbackQueryHandler(buton_tiklama_yoneticisi))

    logger.info("✅ Bot başarıyla ayağa kalktı. DM Yönlendirmeli Profesyonel Parti Sistemi Aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
