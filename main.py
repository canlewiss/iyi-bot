import os
import io
import logging
from collections import defaultdict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --------------------------------------------------
# ENV
# --------------------------------------------------
TOKEN = "8855568852:AAG8I-2B_ZjkWQVIR5a4GL0PjzyyR5aZ3kg"
PARTI_GRUP_ID = int(os.getenv("PARTI_GRUP_ID", "0"))
PARTI_KONU_ID = int(os.getenv("PARTI_KONU_ID", "0"))

YONETICILER = {
    7924242319,
    1293227694,
    5656861374
}

# --------------------------------------------------
# RAM DATABASE
# --------------------------------------------------
class DB:
    def __init__(self):
        self.aktif = False
        self.tarih = None
        self.kayit = {}  # uid -> {isim, parti}
        self.sira = []   # ilk kayıt sırası
        self.state = {}  # uid -> state
        self.yasak = {"aq", "amk", "oç", "piç", "lan"}

db = DB()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def admin(uid: int):
    return uid in YONETICILER


def puan(uid: int):
    if uid not in db.kayit:
        return 0

    data = db.kayit[uid]
    base = data["parti"] * 10

    if uid in db.sira:
        i = db.sira.index(uid)
        bonus = {0: 30, 1: 20, 2: 10}.get(i, 0)
        return base + bonus

    return base


def reset_event():
    db.aktif = False
    db.tarih = None
    db.kayit.clear()
    db.sira.clear()

# --------------------------------------------------
# START
# --------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Sunday City Bot\n\n"
        "/kayit - kayıt ol\n"
        "/durum - durum\n"
        "/puanim - puan\n"
    )

# --------------------------------------------------
# KAYIT
# --------------------------------------------------
async def kayit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.aktif:
        await update.message.reply_text("❌ Aktif parti yok.")
        return

    uid = update.effective_user.id
    db.state[uid] = {"step": "isim"}

    await update.message.reply_text("🎮 İsim gir:")

# --------------------------------------------------
# DURUM
# --------------------------------------------------
async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in db.kayit:
        await update.message.reply_text("Kayıt yok.")
        return

    d = db.kayit[uid]
    await update.message.reply_text(
        f"🎮 {d['isim']}\n🎉 Parti: {d['parti']}"
    )

# --------------------------------------------------
# PUAN
# --------------------------------------------------
async def puanim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    await update.message.reply_text(f"🏆 Puan: {puan(uid)}")

# --------------------------------------------------
# MENU
# --------------------------------------------------
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not admin(uid):
        return

    kb = [
        [InlineKeyboardButton("🎉 Parti Kur", callback_data="kur")],
        [InlineKeyboardButton("📄 Liste", callback_data="liste")],
        [InlineKeyboardButton("🏆 Puanlar", callback_data="puan")],
        [InlineKeyboardButton("🚫 Sıfırla", callback_data="reset")]
    ]

    await update.message.reply_text(
        "⚙ Admin Panel",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# --------------------------------------------------
# CALLBACK
# --------------------------------------------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    if not admin(uid):
        return

    if q.data == "kur":
        reset_event()
        db.state[uid] = {"step": "tarih"}
        await q.edit_message_text("📅 Tarih gir:")

    elif q.data == "reset":
        reset_event()
        await q.edit_message_text("🚫 Sistem sıfırlandı.")

    elif q.data == "liste":
        if not db.kayit:
            await q.edit_message_text("Boş liste.")
            return

        text = "\n".join(
            f"{v['isim']} - {v['parti']} parti"
            for v in db.kayit.values()
        )

        file = io.BytesIO(text.encode())
        file.name = "liste.txt"

        await q.message.reply_document(InputFile(file))

    elif q.data == "puan":
        if not db.kayit:
            await q.edit_message_text("Boş.")
            return

        s = sorted(
            db.kayit.items(),
            key=lambda x: puan(x[0]),
            reverse=True
        )

        msg = "🏆 PUAN TABLOSU\n\n"
        for uid2, v in s:
            msg += f"{v['isim']} - {puan(uid2)}\n"

        await q.edit_message_text(msg)

# --------------------------------------------------
# MESSAGE HANDLER
# --------------------------------------------------
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    uid = update.effective_user.id
    text = update.message.text

    if any(x in text.lower() for x in db.yasak):
        await update.message.delete()
        return

    if uid not in db.state:
        return

    step = db.state[uid]["step"]

    # ---------------- TARIH ----------------
    if step == "tarih":
        db.tarih = text
        db.aktif = True
        del db.state[uid]

        bot = await context.bot.get_me()
        link = f"https://t.me/{bot.username}?start=kayit"

        await context.bot.send_message(
            PARTI_GRUP_ID,
            message_thread_id=PARTI_KONU_ID,
            text=f"🎉 Yeni Parti\n📅 {text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Kayıt Ol", url=link)]
            ])
        )

        await update.message.reply_text("✅ Parti açıldı.")

    # ---------------- ISIM ----------------
    elif step == "isim":
        db.state[uid] = {"step": "parti", "isim": text}
        await update.message.reply_text("🎉 Kaç parti?")

    # ---------------- PARTI ----------------
    elif step == "parti":
        if not text.isdigit():
            await update.message.reply_text("Sadece sayı gir.")
            return

        isim = db.state[uid]["isim"]
        yeni = uid not in db.kayit

        db.kayit[uid] = {
            "isim": isim,
            "parti": int(text)
        }

        if yeni:
            db.sira.append(uid)

        del db.state[uid]

        await update.message.reply_text(
            f"✅ Kayıt OK\n🏷 {isim}\n🎉 {text} parti\n🏆 {puan(uid)} puan"
        )

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kayit", kayit))
    app.add_handler(CommandHandler("durum", durum))
    app.add_handler(CommandHandler("puanim", puanim))
    app.add_handler(CommandHandler("menu", menu))

    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    print("Bot aktif...")
    app.run_polling()

if __name__ == "__main__":
    main()
