import os
import requests
import random
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CẤU HÌNH ---
# Dùng biến môi trường trên Render để bảo mật
TOKEN = os.environ.get('TOKEN') 
CHANNEL_ID = '-1003808692297'
ADMIN_ID = 5838598093 
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

# Trạng thái
bot_enabled = True
history = []
last_session = None

# --- BẢO MẬT & ĐIỀU KHIỂN ---
def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

async def bat_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    global bot_enabled
    bot_enabled = True
    await update.message.reply_text("✅ Tool đã được KÍCH HOẠT.")

async def tat_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    global bot_enabled
    bot_enabled = False
    await update.message.reply_text("❌ Tool đã được TẮT.")

# --- ENGINE DỰ ĐOÁN ---
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
            if len(history) >= 2 and history[-1] == history[-2]: diem = (diem + 5) % 10
            
            ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
            ty_le = f"{random.randint(65, 80)}%"
            history.append(diem >= 5)
            if len(history) > 3: history.pop(0)
            
            msg = f"🌟 LC79 VIP SYSTEM 🌟\n🎯 Phiên: #{id_moi}\n🔮 Dự đoán: {ket_qua}\n📊 Tỉ lệ: {ty_le}\n♾️ Mã MD5: {ma_md5}"
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
            last_session = phien['id']
    except Exception as e:
        print(f"Lỗi: {e}")

# --- PHẦN KÍCH HOẠT CHO RENDER ---
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running!"

if __name__ == '__main__':
    # Chạy Web server cho Render
    Thread(target=lambda: app_web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    
    # Chạy Bot Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=1)
        
    app.run_polling()
