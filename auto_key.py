import json
import os
import time
import random
import string
from datetime import datetime, timedelta
import requests # type: ignore

KEY_FILE = "daily_keys.json"
API_KEY = "66c86fffe7c17e3a7e6b9a35"  # <- Chỉ giữ lại mã token
BOT_USERNAME = "md5v1vip_bot"    # <- Thay bằng username thật của bot bạn

def generate_key(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def load_keys():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_keys(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def shorten_link(long_url):
    try:
        api_url = f"https://link4m.co/api-shorten/v2?api={API_KEY}&url={long_url}"
        res = requests.get(api_url)
        data = res.json()
        return data.get("shortenedUrl")
    except Exception as e:
        print("❌ Lỗi rút gọn link:", e)
        return long_url

def run():
    print("🔑 auto_key.py đang chạy...")
    while True:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        keys_data = load_keys()
        user_ids = ["7149801073"]  # 👈 Danh sách user được tạo key mỗi ngày

        changed = False
        for user_id in user_ids:
            if user_id in keys_data and keys_data[user_id]["date"] == today:
                continue  # đã có key hôm nay

            key = generate_key()
            link = f"https://t.me/{BOT_USERNAME}?start=key_{key}"
            short = shorten_link(link)
            expires = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

            keys_data[user_id] = {
                "key": key,
                "short_url": short,
                "expires": expires,
                "date": today
            }
            print(f"✅ Tạo key cho {user_id}: {key} - {short}")
            changed = True

        # Xoá user hết hạn
        for uid in list(keys_data):
            exp = datetime.strptime(keys_data[uid]["expires"], "%Y-%m-%d %H:%M:%S")
            if datetime.utcnow() > exp:
                print(f"🧹 Xóa user hết hạn: {uid}")
                del keys_data[uid]
                changed = True

        if changed:
            save_keys(keys_data)

        time.sleep(60 * 5)  # chạy lại mỗi 5 phút

if __name__ == "__main__":
    run()
