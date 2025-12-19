import re
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# THAY TOKEN CỦA BẠN VÀO ĐÂY
BOT_TOKEN = "7987929868:AAEsLHkOhZEIGXdg4Aw-_lvOTQXClknZGw4"

# Biến tạm lưu dữ liệu user
user_data = {}

def parse_input(text):
    parts = text.split()
    date_match = re.search(r'(\d{1,2}/\d{1,2})', text)
    date = date_match.group(1) if date_match else ""
    
    dac_biet = 0
    super_tt = 0
    vip_tt = 0
    super_bt = 0
    tip_nv = 0
    da_ck = 0
    
    combined_text = " ".join(parts).lower()
    
    # Tìm vé đặc biệt
    db_match = re.search(r'(\d+)\s*dacbiet', combined_text)
    if db_match:
        dac_biet = int(db_match.group(1))
    
    # Tìm SuperTT
    super_match = re.search(r'(\d+)\s*super', combined_text)
    if super_match:
        super_tt = int(super_match.group(1))
    
    # Tìm VipTT
    vip_match = re.search(r'(\d+)\s*vip', combined_text)
    if vip_match:
        vip_tt = int(vip_match.group(1))
    
    # Tìm SuperBT
    bt_match = re.search(r'(\d+)\s*v500', combined_text)
    if bt_match:
        super_bt = int(bt_match.group(1))
    
    # Tìm tiền tip và đã chuyển khoản
    for i, part in enumerate(parts):
        part_lower = part.lower()
        if 'cknv' in part_lower:
            if i < len(parts)-1 and parts[i+1].isdigit():
                tip_nv = int(parts[i+1]) * 1000
        elif 'dack' in part_lower:
            if i < len(parts)-1 and parts[i+1].isdigit():
                da_ck = int(parts[i+1]) * 1000
    
    return {
        'date': date,
        'dac_biet': dac_biet,
        'super_tt': super_tt,
        'vip_tt': vip_tt,
        'super_bt': super_bt,
        'tip_nv': tip_nv,
        'da_ck': da_ck
    }

def calculate_revenue(data):
    dac_biet_revenue = data['dac_biet'] * 1700000
    super_tt_revenue = data['super_tt'] * 700000
    vip_tt_revenue = data['vip_tt'] * 600000
    super_bt_revenue = data['super_bt'] * 500000
    
    total_ve = data['dac_biet'] + data['super_tt'] + data['vip_tt'] + data['super_bt']
    total_revenue = dac_biet_revenue + super_tt_revenue + vip_tt_revenue + super_bt_revenue
    
    tien_goc = (data['dac_biet'] * 1100000 + 
                (data['super_tt'] + data['vip_tt']) * 400000 + 
                data['super_bt'] * 500000)
    
    tien_ngon_nv = total_revenue - tien_goc
    total_ve_tip = total_revenue + data['tip_nv']
    tien_mat = total_ve_tip - data['da_ck']
    
    return {
        'dac_biet_revenue': dac_biet_revenue,
        'super_tt_revenue': super_tt_revenue,
        'vip_tt_revenue': vip_tt_revenue,
        'super_bt_revenue': super_bt_revenue,
        'total_ve': total_ve,
        'total_revenue': total_revenue,
        'tien_goc': tien_goc,
        'tien_ngon_nv': tien_ngon_nv,
        'total_ve_tip': total_ve_tip,
        'tien_mat': tien_mat
    }

def format_currency(amount):
    return f"{amount:,.0f}".replace(",", ".")

def format_output(data, calc_data):
    output_lines = []
    
    if data['dac_biet'] > 0:
        output_lines.append(f"{data['dac_biet']}vé Đặt biệt*1700 = {format_currency(calc_data['dac_biet_revenue'])}đ")
    
    if data['super_tt'] > 0:
        output_lines.append(f"{data['super_tt']}vé SuperTT*700 = {format_currency(calc_data['super_tt_revenue'])}đ")
    
    if data['vip_tt'] > 0:
        output_lines.append(f"{data['vip_tt']}vé VipTT*600 = {format_currency(calc_data['vip_tt_revenue'])}đ")
    
    if data['super_bt'] > 0:
        output_lines.append(f"{data['super_bt']}vé SuperBT*500 = {format_currency(calc_data['super_bt_revenue'])}đ")
    
    ve_lines = "\n".join(output_lines)
    
    output = f"""Dạ anh Ba doanh thu Massage Royal An An ngày {data['date']} gồm :

{ve_lines}

Tổng {calc_data['total_ve']}vé = {format_currency(calc_data['total_revenue'])}đ
Tiền gốc : {format_currency(calc_data['tien_goc'])}đ
Tiền ngọn NV : {format_currency(calc_data['tien_ngon_nv'])}đ
Tiền khách tip thêm NV : {format_currency(data['tip_nv'])}đ
Tổng tiền vé + tip : {format_currency(calc_data['total_ve_tip'])}đ
Đã ck trước a Ba : {format_currency(data['da_ck'])}đ
Còn lại tiền mặt : {format_currency(calc_data['tien_mat'])}đ"""
    
    return output

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là bot tính toán doanh thu Massage Royal An An.\n\n"
        "Hãy gửi dữ liệu theo định dạng:\n"
        "14/11 10dacbiet 1super 4vip 13v500 cknv 4600 dack 10100\n\n"
        "Hoặc dùng lệnh /nhanh để nhập liệu nhanh bằng button!"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xóa tất cả tin nhắn trong cuộc trò chuyện"""
    try:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        
        # Xóa tin nhắn lệnh /clear
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        
        # Gửi lại lời mở đầu
        await context.bot.send_message(
            chat_id=chat_id,
            text="Xin chào! Tôi là bot tính toán doanh thu Massage Royal An An.\n\n"
                 "Hãy gửi dữ liệu theo định dạng:\n"
                 "14/11 10dacbiet 1super 4vip 13v500 cknv 4600 dack 10100\n\n"
                 "Hoặc dùng lệnh /nhanh để nhập liệu nhanh bằng button!"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Không thể xóa tin nhắn: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        
        # Kiểm tra nếu đang trong chế độ nhập button
        if 'waiting_for' in context.user_data:
            await handle_button_input(update, context)
            return
            
        parsed_data = parse_input(user_text)
        calculated_data = calculate_revenue(parsed_data)
        output = format_output(parsed_data, calculated_data)
        await update.message.reply_text(output)
        
    except Exception as e:
        await update.message.reply_text(f"Có lỗi xảy ra: {str(e)}\nVui lòng kiểm tra lại định dạng dữ liệu.")

# ==================== PHẦN BUTTON NHẬP LIỆU NHANH ====================

async def quick_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập liệu nhanh bằng button"""
    user_id = update.message.from_user.id
    
    # Khởi tạo dữ liệu user nếu chưa có
    if user_id not in user_data:
        user_data[user_id] = {
            'date': datetime.datetime.now().strftime("%d/%m"),
            'dac_biet': 0, 'super_tt': 0, 'vip_tt': 0, 
            'super_bt': 0, 'tip_nv': 0, 'da_ck': 0
        }
    
    current_data = user_data[user_id]
    
    # Tạo keyboard button
    keyboard = [
        [InlineKeyboardButton("📅 Ngày: " + current_data['date'], callback_data="select_date")],
        [
            InlineKeyboardButton("🎫 ĐB: " + str(current_data['dac_biet']), callback_data="add_dacbiet"),
            InlineKeyboardButton("⭐ Super: " + str(current_data['super_tt']), callback_data="add_super")
        ],
        [
            InlineKeyboardButton("💎 Vip: " + str(current_data['vip_tt']), callback_data="add_vip"),
            InlineKeyboardButton("🔹 BT: " + str(current_data['super_bt']), callback_data="add_bt")
        ],
        [InlineKeyboardButton("💰 Tip: " + format_currency(current_data['tip_nv']), callback_data="add_tip")],
        [InlineKeyboardButton("🏦 Đã CK: " + format_currency(current_data['da_ck']), callback_data="add_dack")],
        [InlineKeyboardButton("🧮 Tính toán", callback_data="calculate"), InlineKeyboardButton("🔄 Reset", callback_data="reset")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Tạo summary
    total_ve = current_data['dac_biet'] + current_data['super_tt'] + current_data['vip_tt'] + current_data['super_bt']
    summary = f"📊 Tổng vé: {total_ve} | "
    summary += f"ĐB: {current_data['dac_biet']} | "
    summary += f"Super: {current_data['super_tt']} | "
    summary += f"Vip: {current_data['vip_tt']} | "
    summary += f"BT: {current_data['super_bt']}"
    
    await update.message.reply_text(
        f"🚀 NHẬP LIỆU NHANH:\n{summary}\n\nChọn loại vé cần thêm:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'date': datetime.datetime.now().strftime("%d/%m"),
            'dac_biet': 0, 'super_tt': 0, 'vip_tt': 0, 
            'super_bt': 0, 'tip_nv': 0, 'da_ck': 0
        }
    
    data = query.data
    current_data = user_data[user_id]
    
    if data == "select_date":
        await query.edit_message_text(
            text="📅 Nhập ngày (ví dụ: 14/11):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="back")]])
        )
        context.user_data['waiting_for'] = 'date'
        
    elif data.startswith("add_"):
        field_name = data.replace('add_', '')
        field_display = {
            'dacbiet': 'Đặc biệt', 
            'super': 'SuperTT', 
            'vip': 'VipTT', 
            'bt': 'SuperBT', 
            'tip': 'Tip NV (nghìn) - Ví dụ: 4600 = 4.600.000đ',
            'dack': 'Đã chuyển khoản (nghìn) - Ví dụ: 7000 = 7.000.000đ'
        }
        await query.edit_message_text(
            text=f"🔢 Nhập số lượng:\n{field_display[field_name]}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại", callback_data="back")]])
        )
        context.user_data['waiting_for'] = field_name
        
    elif data == "calculate":
        # Tính toán và hiển thị kết quả
        if current_data['date'] and (current_data['dac_biet'] > 0 or current_data['super_tt'] > 0 or current_data['vip_tt'] > 0 or current_data['super_bt'] > 0):
            calculated_data = calculate_revenue(current_data)
            output = format_output(current_data, calculated_data)
            await query.edit_message_text(output)
            # Reset data sau khi tính
            user_data[user_id] = {
                'date': datetime.datetime.now().strftime("%d/%m"),
                'dac_biet': 0, 'super_tt': 0, 'vip_tt': 0, 
                'super_bt': 0, 'tip_nv': 0, 'da_ck': 0
            }
        else:
            await query.edit_message_text(
                "❌ Chưa có đủ dữ liệu! Vui lòng nhập ít nhất 1 loại vé.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Thử lại", callback_data="back")]])
            )
        
    elif data == "reset":
        # Reset dữ liệu
        user_data[user_id] = {
            'date': datetime.datetime.now().strftime("%d/%m"),
            'dac_biet': 0, 'super_tt': 0, 'vip_tt': 0, 
            'super_bt': 0, 'tip_nv': 0, 'da_ck': 0
        }
        await quick_input(update, context)
        
    elif data == "back":
        await quick_input(update, context)

async def handle_button_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input số lượng từ button"""
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("❌ Phiên làm việc đã hết hạn. Gõ /nhanh để bắt đầu lại.")
        return
    
    if 'waiting_for' not in context.user_data:
        await update.message.reply_text("❌ Lỗi hệ thống. Gõ /nhanh để bắt đầu lại.")
        return
    
    field = context.user_data['waiting_for']
    text = update.message.text.strip()
    
    try:
        if field == 'date':
            # Validate date format
            if re.match(r'\d{1,2}/\d{1,2}', text):
                user_data[user_id]['date'] = text
                await update.message.reply_text(f"✅ Đã đặt ngày: {text}")
            else:
                await update.message.reply_text("❌ Định dạng ngày sai (ví dụ: 14/11)")
                return
        else:
            # Validate number
            number = int(text)
            if field == 'dacbiet':
                user_data[user_id]['dac_biet'] = number
                display_text = f"Đặc biệt: {number} vé"
            elif field == 'super':
                user_data[user_id]['super_tt'] = number
                display_text = f"SuperTT: {number} vé"
            elif field == 'vip':
                user_data[user_id]['vip_tt'] = number
                display_text = f"VipTT: {number} vé"
            elif field == 'bt':
                user_data[user_id]['super_bt'] = number
                display_text = f"SuperBT: {number} vé"
            elif field == 'tip':
                user_data[user_id]['tip_nv'] = number * 1000
                display_text = f"Tip NV: {format_currency(number * 1000)}đ"
            elif field == 'dack':
                user_data[user_id]['da_ck'] = number * 1000
                display_text = f"Đã CK: {format_currency(number * 1000)}đ"
            
            await update.message.reply_text(f"✅ {display_text}")
        
        # Xóa trạng thái chờ
        del context.user_data['waiting_for']
        
        # Quay lại menu chính
        await quick_input(update, context)
        
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số hợp lệ!")

def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Lỗi: Chưa đặt BOT_TOKEN trong code!")
        return
    
    print("Đang khởi động bot...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_chat))
    application.add_handler(CommandHandler("nhanh", quick_input))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
