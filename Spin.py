import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== TOKEN TỪ BIẾN MÔI TRƯỜNG ======
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ====== SLOT CONFIG ======
SYMBOLS = ["🍒", "🍋", "🔔", "⭐", "7"]
WEIGHTS = [40, 30, 20, 9, 1]
BET = 100_000

WIN_MULTIPLIER = {
    "🍒": 2,
    "🍋": 3,
    "🔔": 5,
    "⭐": 10,
    "7": 50
}

users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {"balance": 1_600_000}
    return users[uid]

def spin(cheat=False):
    if cheat:
        return ["7"] * 5
    return random.choices(SYMBOLS, weights=WEIGHTS, k=5)

def check_win(reels):
    if len(set(reels)) == 1:
        return BET * WIN_MULTIPLIER[reels[0]]
    return 0

# ====== COMMANDS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎰 SLOT BOT (MÔ PHỎNG)\n"
        "/spin – Quay\n"
        "/balance – Số dư\n"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 {user['balance']:,}")

async def spin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user["balance"] < BET:
        await update.message.reply_text("❌ Hết tiền!")
        return

    user["balance"] -= BET
    reels = spin()
    win = check_win(reels)

    text = " ".join(f"[{s}]" for s in reels)

    if win:
        user["balance"] += win
        await update.message.reply_text(
            f"{text}\n🎉 +{win:,}\n💰 {user['balance']:,}"
        )
    else:
        await update.message.reply_text(
            f"{text}\n❌ Thua\n💰 {user['balance']:,}"
        )

# ====== MAIN ======
def main():
    if not BOT_TOKEN:
        print("❌ Chưa set BOT_TOKEN")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("spin", spin_cmd))
    app.add_handler(CommandHandler("balance", balance))

    print("🤖 BOT ĐANG CHẠY...")
    app.run_polling()

if __name__ == "__main__":
    main()
