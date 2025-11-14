import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# THAY TOKEN CỦA BẠN VÀO ĐÂY
BOT_TOKEN = "7987929868:AAHN4BFkS9iEnoyoZmDCm5WP9qS5mD4Hki0"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Royal An An đang hoạt động! Gửi dữ liệu theo định dạng: 14/11 10super 5vip 1v500")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        await update.message.reply_text(f"📊 Đã nhận dữ liệu: {text}\n\nBot đang xử lý...")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}")

def main():
    print("🔄 Đang khởi động bot...")
    
    if BOT_TOKEN == "7987929868:AAHN4BFkS9iEnoyoZmDCm5WP9qS5mD4Hki0":
        print("❌ Lỗi: Chưa đặt BOT_TOKEN trong code!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
