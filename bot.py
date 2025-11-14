import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ĐẶT TOKEN TRỰC TIẾP Ở ĐÂY - THAY YOUR_BOT_TOKEN bằng token thật
BOT_TOKEN = "7987929868:AAHN4BFkS9iEnoyoZmDCm5WP9qS5mD4Hki0"  # 👈 THAY TOKEN Ở ĐÂY

def parse_input(text):
    # Tách các phần từ input
    parts = text.split()
    
    # Tìm ngày
    date_match = re.search(r'(\d{1,2}/\d{1,2})', text)
    date = date_match.group(1) if date_match else ""
    
    # Tìm các loại vé
    dac_biet = 0  # 4tay
    super_tt = 0
    vip_tt = 0
    super_bt = 0
    tip_nv = 0
    da_ck = 0
    
    # Ghép các phần lại để xử lý trường hợp có khoảng trống
    combined_text = " ".join(parts).lower()
    
    # Tìm vé đặc biệt (dacbiet)
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
            # Tìm tiền tip NV
            if i < len(parts)-1 and parts[i+1].isdigit():
                tip_nv = int(parts[i+1]) * 1000
        elif 'dack' in part_lower:
            # Tìm tiền đã chuyển
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
    # Tính toán doanh thu (đơn vị: đồng)
    dac_biet_revenue = data['dac_biet'] * 1700000
    super_tt_revenue = data['super_tt'] * 700000
    vip_tt_revenue = data['vip_tt'] * 600000
    super_bt_revenue = data['super_bt'] * 500000
    
    total_ve = data['dac_biet'] + data['super_tt'] + data['vip_tt'] + data['super_bt']
    total_revenue = dac_biet_revenue + super_tt_revenue + vip_tt_revenue + super_bt_revenue
    
    # Tính tiền gốc (đơn vị: đồng)
    tien_goc = (data['dac_biet'] * 1100000 + 
                (data['super_tt'] + data['vip_tt']) * 400000 + 
                data['super_bt'] * 500000)
    
    # Tiền ngọn = Tổng doanh thu - Tiền gốc
    tien_ngon_nv = total_revenue - tien_goc
    
    # Tổng tiền vé + tip
    total_ve_tip = total_revenue + data['tip_nv']
    
    # Tính toán số tiền còn lại
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
    """Format số tiền với dấu . làm phân cách hàng nghìn"""
    return f"{amount:,.0f}".replace(",", ".")

def format_output(data, calc_data):
    output_lines = []
    
    # Tạo phần vé đặc biệt nếu có
    if data['dac_biet'] > 0:
        output_lines.append(f"{data['dac_biet']}vé Đặt biệt*1700 = {format_currency(calc_data['dac_biet_revenue'])}đ")
    
    # Tạo phần SuperTT nếu có
    if data['super_tt'] > 0:
        output_lines.append(f"{data['super_tt']}vé SuperTT*700 = {format_currency(calc_data['super_tt_revenue'])}đ")
    
    # Tạo phần VipTT nếu có
    if data['vip_tt'] > 0:
        output_lines.append(f"{data['vip_tt']}vé VipTT*600 = {format_currency(calc_data['vip_tt_revenue'])}đ")
    
    # Tạo phần SuperBT nếu có
    if data['super_bt'] > 0:
        output_lines.append(f"{data['super_bt']}vé SuperBT*500 = {format_currency(calc_data['super_bt_revenue'])}đ")
    
    # Ghép các dòng vé
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
        "Công thức tính:\n"
        "• Đặc biệt (dacbiet): 1.700.000đ/vé (Gốc: 1.100.000đ, Ngọn: 600.000đ)\n"
        "• SuperTT: 700.000đ/vé (Gốc: 400.000đ, Ngọn: 300.000đ)\n"
        "• VipTT: 600.000đ/vé (Gốc: 400.000đ, Ngọn: 200.000đ)\n"
        "• SuperBT: 500.000đ/vé (Gốc: 500.000đ, Ngọn: 0đ)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        
        # Parse dữ liệu đầu vào
        parsed_data = parse_input(user_text)
        
        # Tính toán doanh thu
        calculated_data = calculate_revenue(parsed_data)
        
        # Format output
        output = format_output(parsed_data, calculated_data)
        
        await update.message.reply_text(output)
        
    except Exception as e:
        await update.message.reply_text(f"Có lỗi xảy ra: {str(e)}\nVui lòng kiểm tra lại định dạng dữ liệu.")

def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("Lỗi: Chưa đặt BOT_TOKEN trong code!")
        return
    
    # Tạo application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Chạy bot
    print("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
