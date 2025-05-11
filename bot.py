import telebot
import json
import os
import time
from datetime import datetime, timedelta
import random
import requests

TOKEN = "7679248695:AAE4zuT0KHnXSf82hXhO_h0ncw7ULeKzDaI"
bot = telebot.TeleBot(TOKEN, parse_mode="MarkdownV2")

ADMIN_ID = 7149801073
KEY_FILE = "daily_keys.json"
USER_FILE = "allowed_users.json"

def escape_md(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# Kiểm tra và tạo file JSON nếu chưa tồn tại
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_keys():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return json.load(f)
    return {}

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_user_allowed(user_id):
    users = load_users()
    now = datetime.utcnow()
    if str(user_id) in users:
        expire = datetime.strptime(users[str(user_id)]["expires"], "%Y-%m-%d %H:%M:%S")
        return now < expire
    return user_id == ADMIN_ID

def analyze_md5(md5_string):
    try:
        md5_int = int(md5_string, 16)
        last_two_digits = md5_int % 100
        result = "🔥TÀI" if last_two_digits >= 50 else "❄️ *XỈU*"
        tai_rate = round((last_two_digits / 99) * 100, 2)
        xiu_rate = 100 - tai_rate
        return escape_md(
            f"🎰 Kết Quả Phân Tích 🎰\n\n"
            f"🔍 MD5 Hash: `{md5_string}`\n"
            f"🎲 Số cuối MD5: `{last_two_digits}`\n"
            f"⚖ Kết quả Là: {result}\n\n"
            f"📊 Xác suất sau khi phân tích:\n"
            f"   - 🎯 Tài: {tai_rate}%\n"
            f"   - ❄️ Xỉu: {xiu_rate}%\n\n"
            f"📩Hãy gửi thêm MD5 để tiếp tục!\n"
            f"🛠Developer:Benz Mod"
        )
    except:
        return escape_md("❌ Mã Lỗi! Vui lòng gửi MD5 hợp lệ.")

@bot.message_handler(commands=['start'])
def start_command(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("key_"):
        key_input = args[1].replace("key_", "")
        user_id = str(message.from_user.id)
        keys = load_keys()
        if user_id in keys and keys[user_id]["key"] == key_input:
            users = load_users()
            users[user_id] = {
                "activated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "expires": keys[user_id]["expires"]
            }
            save_users(users)
            expires = keys[user_id]["expires"]
            return bot.reply_to(
                message,
                escape_md(f"✅ Kích hoạt thành công từ link!\n🕒 Sử dụng bot đến: `{expires}` (UTC)"),
                parse_mode="MarkdownV2"
            )
        else:
            return bot.reply_to(message, escape_md("❌ Key không hợp lệ hoặc không dành cho bạn."), parse_mode="MarkdownV2")
    bot.reply_to(message, escape_md("👋 Chào mừng bạn Nhé! Hãy Gửi chuỗi MD5 để tôi phân tích."), parse_mode="MarkdownV2")

@bot.message_handler(commands=['id'])
def get_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, escape_md(f"🆔 User ID của bạn: `{user_id}`"), parse_mode="MarkdownV2")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📌 LIST COMMAND 📌\n\n"
        "🔹 /start - Bắt đầu bot\n"
        "🔹 /help - Hiển thị lệnh\n"
        "🔹 /id - Lấy ID người dùng\n"
        "🔹 /add <key> - Kích hoạt bot\n"
        "🔹 /getkey - Nhận key miễn phí"
    )
    if message.from_user.id == ADMIN_ID:
        help_text += (
            "\n\n👑 ADMIN 👑\n"
            "✅ /adduser <id> - Thêm người dùng\n"
            "❌ /removeuser <id> - Xoá người dùng\n"
            "📋 /listusers - Danh sách người dùng\n"
            "📢 /broadcast <msg> - Gửi thông báo"
        )
    bot.reply_to(message, escape_md(help_text), parse_mode="MarkdownV2")

@bot.message_handler(commands=['getkey'])
def getkey_handler(message):
    def save_keys(data):
        with open(KEY_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def generate_key(length=8):
        return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=length))

    def shorten_link(long_url):
        try:
            API_KEY = "66c86fffe7c17e3a7e6b9a35"
            api_url = f"https://link4m.co/api-shorten/v2?api={API_KEY}&url={long_url}"
            res = requests.get(api_url)
            return res.json().get("shortenedUrl", long_url)
        except:
            return long_url

    user_id = str(message.from_user.id)
    keys = load_keys()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if user_id not in keys or keys[user_id]["date"] != today:
        key = generate_key()
        link = f"https://t.me/md5v1vip_bot?start=key_{key}"
        short_url = shorten_link(link)
        expires = (datetime.utcnow() + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        keys[user_id] = {
            "key": key,
            "short_url": short_url,
            "expires": expires,
            "date": today
        }
        save_keys(keys)

    reply_text = (
        f"🔗 Link key của bạn:\n👉 {keys[user_id]['short_url']}\n"
        f"🕒 Key dùng được đến: {keys[user_id]['expires']}"
    )
    bot.reply_to(message, escape_md(reply_text), parse_mode="MarkdownV2")

@bot.message_handler(commands=['add'])
def add_key_user(message):
    try:
        user_id = str(message.from_user.id)
        key_input = message.text.split()[1]
        keys = load_keys()
        if user_id in keys and keys[user_id]['key'] == key_input:
            users = load_users()
            users[user_id] = {
                "activated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "expires": keys[user_id]["expires"]
            }
            save_users(users)
            bot.reply_to(message, escape_md("✅ Kích hoạt thành công! Dùng bot trong 6 giờ."), parse_mode="MarkdownV2")
        else:
            bot.reply_to(message, escape_md("❌ Key không đúng hoặc không phải của bạn."), parse_mode="MarkdownV2")
    except:
        bot.reply_to(message, escape_md("⚠️ Sai cú pháp. Dùng: /add <key>"), parse_mode="MarkdownV2")

@bot.message_handler(func=lambda msg: len(msg.text) == 32 and all(c in "0123456789abcdefABCDEF" for c in msg.text))
def md5_handler(message):
    if not is_user_allowed(message.from_user.id):
        return bot.reply_to(message, escape_md("🚫 Bạn chưa kích hoạt key! Dùng /add <key của bạn>."), parse_mode="MarkdownV2")
    bot.reply_to(message, analyze_md5(message.text), parse_mode="MarkdownV2")

def clean_expired_users():
    users = load_users()
    now = datetime.utcnow()
    changed = False
    for uid in list(users):
        expire = datetime.strptime(users[uid]["expires"], "%Y-%m-%d %H:%M:%S")
        if now > expire:
            del users[uid]
            changed = True
    if changed:
        save_users(users)

# Chạy bot
while True:
    clean_expired_users()
    try:
        print("🤖 Bot đang chạy...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"⚠️ Lỗi: {e}")
        time.sleep(5)
