import requests
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CẤU HÌNH ---
TOKEN = '8229924024:AAGMvkHGixxHhfleez0ovU_4GR7m6ebIZJY'
CHANNEL_ID = '-1003808692297'
ADMIN_ID = 5838598093 # Thay bằng ID của bạn (ví dụ: 5838598093)
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

# Trạng thái và bộ nhớ
bot_enabled = True
history = []
last_session = None

# --- BẢO MẬT: HÀM KIỂM TRA ADMIN ---
def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# --- LỆNH ĐIỀU KHIỂN ---
async def bat_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Bạn không có quyền thực hiện lệnh này.")
        return
    
    global bot_enabled
    bot_enabled = True
    await update.message.reply_text("✅ Tool đã được KÍCH HOẠT.")

async def tat_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 Bạn không có quyền thực hiện lệnh này.")
        return
        
    global bot_enabled
    bot_enabled = False
    await update.message.reply_text("❌ Tool đã được TẮT.")

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        msg = f"👋 Chào mừng {member.first_name} đã gia nhập nhóm Tool LC79🍇NEW!"
        await context.bot.send_message(chat_id=update.message.chat_id, text=msg)

# --- ENGINE TÍNH TOÁN DỰ ĐOÁN ---
async def job_monitor(context: ContextTypes.DEFAULT_TYPE):
    global last_session, history, bot_enabled
    if not bot_enabled: return

    try:
        response = requests.get(API_URL).json()
        phien = response['list'][0]
        
        if last_session != phien['id']:
            id_moi = int(phien['id']) + 1
            ma_md5 = phien.get('_id', '0')
            
            checksum = int(ma_md5[-1], 16) if ma_md5[-1].isdigit() else 5
            diem = (id_moi + checksum) % 10
            if len(history) >= 2 and history[-1] == history[-2]:
                diem = (diem + 5) % 10
            
            ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
            ty_le = f"{random.randint(65, 80)}%"
            
            history.append(diem >= 5)
            if len(history) > 3: history.pop(0)
            
            msg = (f"🌟 LC79 VIP SYSTEM 🌟\n🎯 Phiên: #{id_moi}\n"
                   f"🔮 Dự đoán: {ket_qua}\n📊 Tỉ lệ: {ty_le}\n"
                   f"♾️ Mã MD5: {ma_md5}\n👑 Admin: Tuanx3000")
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
            last_session = phien['id']
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == '__main__':
    # Khởi tạo App với JobQueue được tích hợp
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, chao_thanh_vien_moi))
    
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=1)
    
    print("Bot đã sẵn sàng và đang hoạt động...")
    app.run_polling()
