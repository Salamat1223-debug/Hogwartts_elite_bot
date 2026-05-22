import json
import logging
import os
import random
import time
from threading import Thread
import requests  # <-- O'z-o'zini uyg'otish so'rovlari uchun kerak
from flask import Flask  # <-- Render o'chib qolmasligi uchun eng yengil veb-server
import telebot
from telebot import types

# --- SOZLAMALAR ---
API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8669459130:AAEiW8ZLeYNuITToXN9vCURiQdS3u5o_r_U")
CHANNEL = "@SaIamatPirjanov"
GROUP = "@SalamatPirjanov_chat"
ADMIN_ID = 7821230725
SHLYAPA_USER = "SalamatPirjanov"

# Render sizga bergan havola (Bot o'zini o'zi uyg'otishi uchun)
RENDER_URL = "https://hogwartts-elite-bot.onrender.com"

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# --- ADMIN STATUSLARI UCHUN ODDIY BAZA (FSM o'rniga) ---
ADMIN_STATES = {}

# --- MA'LUMOTLAR BAZASI ---
ALL_IN_ONE_BOOK = {"name": "📚 Hammasi birda (1-7)", "file_id": "BQACAgIAAxkBAAILb2njPA6Fk6cOMRTWHddACR7gPuodAAI0HwACIynpS2_wVwpElnx4OwQ", "caption": "📚 Garri Potter: Barcha qismlar (1-7) bitta faylda!\n\n📢 Kanal: @harry_potter_fans_uz"}

BOOKS_UZ = [
    {"name": "📖 1. Falsafiy tosh", "file_id": "BQACAgIAAxkBAANBacuvW5b3Swv7_h1BWKHAr9BSFDEAAnAAA0vfYUn_DvBFWXk9WToE", "caption": "📖 Nomi: Garri Potter va Falsafiy tosh\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 2. Maxfiy xujra", "file_id": "BQACAgIAAxkBAANGacuv4uq6XXW9EVN4c1mrczrhf4AAAi4AAwSsEEpZs7eKKsu6szoE", "caption": "📖 Nomi: Garri Potter va Maxfiy hujra\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 3. Azkaban maxbusi", "file_id": "BQACAgIAAxkBAANlacuwQSg_C6sntUxgp1s-EwTRw10AAgkHAAJfZdhIu3sjwnyKCrQ6BA", "caption": "📖 Nomi: Garri Potter va Azkaban mahbusi\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 4. Otashli jom", "file_id": "BQACAgIAAxkBAANnacuwaXcFuxDS8ll0QQ8YYgjxNxcAAjMAAwSsEEoCrCr_9txjwDoE", "caption": "📖 Nomi: Garri Potter va Otashli jom\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 5. Kaknus ordeni", "file_id": "BQACAgIAAxkBAANpacuwkFa_xAhxOPRwz6_O5mhZzkMAAmsAA-A7GEoe0fZOrviJXjoE", "caption": "📖 Nomi: Garri Potter va Kaknus ordeni\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 6. Chalazot shaxzoda", "file_id": "BQACAgIAAxkBAANracuwqVy7l3UaOeEsHvDN8DYyYK4AApIAAzXcUEotF3tao-vWxToE", "caption": "📖 Nomi: Garri Potter va Chalazot shahzoda\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 7. Ajal tuhfalari", "file_id": "BQACAgIAAxkBAANtacuwwS1FlLl5SubbQJDSn6ghyyoAAg8CAAKpCIBJRzBcQ4IMdzA6BA", "caption": "📖 Nomi: Garri Potter va Ajal tuhfalari 1\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 8. La'natlangan bola 1", "file_id": "BQACAgEAAxkBAAIMY2njQ5k79S8QVqRQiST5HpVRcL51AALqAANhXKhHO6BAQyik9OU7BA", "caption": "📖 Nomi: Garri Potter va Laʼnatlangan bola 1 \n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 9. La'natlangan bola 2", "file_id": "BQACAgIAAxkBAAIMcWnjRJdRRTbQJwABUlIFzTOmhHJx1AACrAIAAi1ZKUi4zsBEGFhMPjsE", "caption": "📖 Nomi: Garri Potter va Laʼnatlangan bola 2 \n\n📢 Kanal: @harry_potter_fans_uz"},
]

BOOKS_EN = [
    {"name": "📖 1. Philosopher's Stone", "file_id": "BQACAgUAAxkBAAIDOWnOk3dbX8E-yaAVFy_xfeP6IqKGAAL_AwACn_N4VR4lpjl-n1tZOgQ", "caption": "📖 Name: Harry Potter 1\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 2. Chamber of Secrets", "file_id": "BQACAgUAAxkBAAIDO2nOk9iTjQ_vULXaRoo7BPiFoyESAAMEAAKf83hV774CCp3aF146BA", "caption": "📖 Name: Harry Potter 2\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 3. Prisoner of Azkaban", "file_id": "BQACAgUAAxkBAAIDPWnOk_jB-bYD-xsrsq6Y1xveD1mBAAL-AwACn_N4Vd-iiVWRVt-DOgQ", "caption": "📖 Name: Harry Potter 3\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 4. Goblet of Fire", "file_id": "BQACAgUAAxkBAAIDP2nOlAzIskBV4m7d6OgD3G1o2FOEAAL7AwACn_N4VdM2NXmcWgR-OgQ", "caption": "📖 Name: Harry Potter 4\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 5. Order of the Phoenix", "file_id": "BQACAgUAAxkBAAIDQWnOlB5zRwpHT1wOS9diXcxjCcogAAL5AwACn_N4VQGCfrTny6GKOgQ", "caption": "📖 Name: Harry Potter 5\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 6. Half-Blood Prince", "file_id": "BQACAgUAAxkBAAIDQ2nOlDGDPZqe9r1QZbUUJDj4-L0UAAL6AwACn_N4VWeuyWoTm2SnOgQ", "caption": "📖 Name: Harry Potter 6\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "ZG 1", "file_id": "BQACAgUAAxkBAAIDRWnOlEOi6oyRRafs-Y9Yl1Lo19fjAAL8AwACn_N4VdOVKXxjV5MlOgQ", "caption": "📖 Name: Harry Potter 7\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "ZG 2", "file_id": "BQACAgUAAxkBAAIDRWnOlEOi6oyRRafs-Y9Yl1Lo19fjAAL8AwACn_N4VdOVKXxjV5MlOgQ", "caption": "📖 Name: Harry Potter 8\n📢 Channel: @harry_potter_fans_uz"},
]

MOVIES_UZ = [
    {"name": "🎬 1. Hikmatlar toshi", "file_id": "BAACAgIAAxkBAAN0acuyGAMCrWD9TTuMq55gFHUM8scAAr2OAAKIIOhKA6wazQylWz46BA", "caption": "🎬 Nomi: HP 1: Hikmatlar toshi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 2. Maxfiy hujra", "file_id": "BAACAgIAAxkBAAOFacu0BPXsr3WF3yYGmJHdjVeDjSMAAmSFAALhnOhKpL77RQyPlaE6BA", "caption": "🎬 Nomi: HP 2: Maxfiy hujra\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 3. Azkoban maxbusi", "file_id": "BAACAgIAAxkBAAILZmnjO1w0gPzN0viW9ZWjDxO1xJxWAAJHhQAC4ZzoShs24A6MhRIQOwQ", "caption": "🎬 Nomi: HP 3: Azkoban maxbusi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 4. Alanga kubogi", "file_id": "BAACAgIAAxkBAAOJacobu1AoUKWQUInEPM0DGXvSZhueUAAqmFAALhnOhKZfF9wiu0Drs6BA", "caption": "🎬 Nomi: HP 4: Alanga kubogi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 5. Feniks jamiyati", "file_id": "BAACAgIAAxkBAAOHacu0W-SHgaTmaKyMu7N7S4D-9NQAAn6FAALhnOhKpYQqLyzBd-k6BA", "caption": "🎬 Nomi: HP 5: Feniks jamiyati\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 6. Tilsim Shahzoda", "file_id": "BAACAgIAAxkBAAONacu1kktAejSVYq9GM3xmHXGzrfAAAoyFAALhnOhKrgZBW8bL1Ws6BA", "caption": "🎬 Nomi: HP 6: Tilsim Shahzoda\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 7. Ajal tuhfasi 1", "file_id": "BAACAgIAAxkBAAOPacu1qaZL-FLQaWMNmAbS1P6B-DUAApeFAALhnOhKF_fANiYvpAk6BA", "caption": "🎬 Nomi: HP 7: Ajal tuhfasi 1\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 8. Ajal tuhfasi 2", "file_id": "BAACAgIAAxkBAAOJacu1AoUKWQUInEPM0DGXvSZhueUAAqmFAALhnOhKZfF9wiu0Drs6BA", "caption": "🎬 Nomi: HP 8: Ajal tuhfasi 2\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
]

MOVIES_RU = [
    {"name": "🎬 1. Философский камень", "file_id": "BAACAgIAAxkBAAIDSWnOlb1_AAGAYgWnEGm3bGJfXjFeggACKAoAAjH_WUs4J1skcGE7GToE", "caption": "🎬 Название: ГП 1: Философский камень\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 2. Тайная комната", "file_id": "BAACAgIAAxkBAAIDS2nOld1zIwQEOIo_XNaB20dS4yBKAAImCgACMf9ZS8YV5UtV-2QLOgQ", "caption": "🎬 Название: ГП 2: Тайная комната\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 3. Узник Азкабана", "file_id": "BAACAgIAAxkBAAIDTWnOlfGGh3F6yuTdkzg6YDll0LciAAInCgACMf9ZSxH4i6-D8wN7OgQ", "caption": "🎬 Название: ГП 3: Узник Азкабана\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 4. Кубок огня", "file_id": "BAACAgIAAxkBAAIDT2nOlgJFMBSJSqBULhYTkSS0dmsdAAIjCgACMf9ZS1Zt8gABJXZpWDoE", "caption": "🎬 Название: ГП 4: Кубок огня\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 5. Орден Феникса", "file_id": "BAACAgQAAxkBAAIDUWnOlhMJxYJ_yWbXZLJ25ZPTS0JJAAKgDAAC2L_JULzvFz_NQdPnOgQ", "caption": "🎬 Название: ГП 5: Орден Феникса\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 6. Принц-полукровка", "file_id": "BAACAgIAAxkBAAIDU2nOliUy9hL1ssJ5e-kORyqEL5DgAAIlCgACMf9ZS2Yi3TnE3abiOgQ", "caption": "🎬 Название: ГП 6: Принц-полукровка\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 7. Дары Смерти 1", "file_id": "BAACAgIAAxkBAAIDVWnOljREOEjf4v0o0Sz2DHs1Zm3xAALpBAACKP2pSAiPJCewUqfUOgQ", "caption": "🎬 Название: ГП 7: Дары Смерти 1\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 8. Дары Смерти 2", "file_id": "BAACAgIAAxkBAAIDV2nOlkSVUkDW2WL6f4WrUmapIQABcQACZQQAAsSsoUjP9fxCTDgDNzoE", "caption": "🎬 Название: ГП 8: Дары Смерти 2\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
]

MOVIES_EN = [
    {"name": "🎬 1. Sorcerer's Stone", "file_id": "BAACAgQAAxkBAAIDWWnOltDBBkgHlm6EC5zZ1__vemdSAAJ_BwACrMaBUKRYUpDTm11oOgQ", "caption": "🎬 Name: HP 1: Sorcerer's Stone\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 2. Chamber of Secrets", "file_id": "BAACAgQAAxkBAAIDW2nOlynvMgKOoF9hn7r8CcccUZo-AAKBBwACrMaBUM7959H4o01HOgQ", "caption": "🎬 Name: HP 2: Chamber of Secrets\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 3. Prisoner of Azkaban", "file_id": "BAACAgQAAxkBAAIDXWnOlz4dtzVGjgW6u9JUz1frSKKNAAKHBwACrMaBUKP9MbVImI-uOgQ", "caption": "🎬 Name: HP 3: Prisoner of Azkaban\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 4. Goblet of Fire", "file_id": "BAACAgQAAxkBAAIDX2nOl0-8b1wOF8VhdnLiVTmx2lQ0AAKOBwACrMaBUNmv6Ega62iuOgQ", "caption": "🎬 Name: HP 4: Goblet of Fire\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 5. Order of the Phoenix", "file_id": "BAACAgYWnOl1-UJIPeUi9iwkH5xveOb1cBAAKVBwACrMaBUC7iNQH-PQokOgQ", "caption": "🎬 Name: HP 5: Order of the Phoenix\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 6. Half-Blood Prince", "file_id": "BAACAgQAAxkBAAIDY2nOl28ipXgwucm7uiCsJ00NrHObAAKNCAACqwKBUHgSmGHyOYgROgQ", "caption": "🎬 Name: HP 6: Half-Blood Prince\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 7. Deathly Hallows 1", "file_id": "BAACAgQAAxkBAAIDZWnOl36nQLjV7TlugAMlJE6y1xFKAAKXCAACqwKBUMiAIxlbsJmOOgQ", "caption": "🎬 Name: HP 7: Deathly Hallows 1\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 8. Deathly Hallows 2", "file_id": "BAACAgQAAxkBAAIDZ2nOl41aUWcgKRzzP_r-suInRRSKAAKkCAACqwKBU733-s2FjB3OgQ", "caption": "🎬 Name: HP 8: Deathly Hallows 2\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
]

HOUSES_DETAILS = {
    "Hufflepuff": {"emoji": "🦡", "kalit": "aql", "txt": "💭 E-eh, men ko'ryapman... \nSadoqat senda birinchi o'rinda. Mehnat qilishdan qo'rqmaysan, do'stlaring uchun joningni berishga tayyorsan."},
    "Gryffindor": {"emoji": "🦁", "kalit": "jasorat", "txt": "🦁 Yuraging to'la qo'rqmaslik. Sen xavf-xatarga tik boqishni bilasan. Jasurlik sening qoningda!"},
    "Slytherin": {"emoji": "🐍", "kalit": "ilon", "txt": "🐍 Buyuklikka intilish... Makr va aqlli munosabat. Sen maqsad sari hech narsadan to'xtamaysan!"},
    "Ravenclaw": {"emoji": "🦅", "kalit": "burgut", "txt": "🦅 O'tkir zehn va bilimga chanqoqlik. Sening aqling har qanday jumboqni yecha oladi!"}
}

# --- BAZA FAYLLARI ---
HOUSES_FILE = "user_houses.json"
USERS_FILE = "users_list.json"
WELCOME_FILE = "welcome_settings.json"
BANNED_FILE = "banned_users.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

# --- FUNKSIYALAR ---
def get_mention(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

def check_sub(user_id):
    try:
        m_ch = bot.get_chat_member(CHANNEL, user_id)
        m_gr = bot.get_chat_member(GROUP, user_id)
        valid = ['member', 'administrator', 'creator']
        return (m_ch.status in valid) and (m_gr.status in valid)
    except Exception as e:
        logging.error(f"Tekshiruvda xato: {e}")
        return True

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📚 Kitoblar"), types.KeyboardButton("🎬 Kinolar"))
    markup.add(types.KeyboardButton("🎩 Saralovchi shlyapa"))
    return markup

def delete_after_delay(chat_id, message_id, delay=600):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# --- JAZO TIZIMI ---
@bot.message_handler(commands=["mute", "ban", "unmute", "unban"])
def handle_punishment(message):
    sender = message.from_user
    mention_sender = get_mention(sender)

    if message.chat.type == 'private' and sender.id == ADMIN_ID:
        cmd = message.text.split()[0]
        args = message.text.replace(cmd, "").strip()
        if cmd == "/ban" and args:
            banned = load_data(BANNED_FILE)
            if not isinstance(banned, list): banned = []
            banned.append(args)
            save_data(BANNED_FILE, list(set(banned)))
            return bot.reply_to(message, f"🚫 Foydalanuvchi ({args}) botdan butunlay haydaldi!")
        elif cmd == "/unban" and args:
            banned = load_data(BANNED_FILE)
            if args in banned:
                banned.remove(args)
                save_data(BANNED_FILE, banned)
                return bot.reply_to(message, f"🕊 Foydalanuvchi ({args}) Azkabandan ozod qilindi!")

    if message.chat.type == 'private': return
    
    try:
        sender_member = bot.get_chat_member(message.chat.id, sender.id)
        is_admin = sender_member.status in ['administrator', 'creator']
    except:
        is_admin = False
    
    if not is_admin:
        return bot.reply_to(message, f"🧙‍♂️ Kechirasiz {mention_sender}, sizda sehrli tayoqcha 🪄 yo'q! Avval sehrli tayoqchaga ega bo'ling.")

    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Sehr ishlatish uchun biror kishiga reply qiling!")

    target = message.reply_to_message.from_user
    mention_target = get_mention(target)
    
    try:
        target_member = bot.get_chat_member(message.chat.id, target.id)
        is_target_admin = target_member.status in ['administrator', 'creator']
    except:
        is_target_admin = False
        
    bot_obj = bot.get_me()

    if is_target_admin or target.id == bot_obj.id:
        return bot.reply_to(message, f"🧙‍♂️ Kechirasiz, {mention_sender} lekin o'zingizni yoki boshqa bir sehrgar adminni jazolash taqiqlangan! Bu Hogwarts qonunlariga zid.")

    msg_text = message.text.split()
    cmd = msg_text[0]
    args = msg_text[1:]
    
    try:
        if cmd == "/ban":
            bot.ban_chat_member(message.chat.id, target.id)
            bot.send_message(message.chat.id, f"🚫 {mention_target} ⛓ Hogwarts o'quvchisi yovuz yo'lga kirgani uchun Azkabanga ravona bo'ldi!")
        
        elif cmd == "/unban":
            bot.unban_chat_member(message.chat.id, target.id)
            bot.send_message(message.chat.id, f"🕊 {mention_target} Azkabandan ozod qilindi!")

        elif cmd == "/mute":
            mute_time = 5
            reason = "Aniqlanmagan"
            
            if args:
                if args[0].isdigit():
                    mute_time = int(args[0])
                    if len(args) > 1:
                        reason = " ".join(args[1:])
                else:
                    reason = " ".join(args)
            
            until_date = int(time.time()) + (mute_time * 60)
            bot.restrict_chat_member(message.chat.id, target.id, until_date=until_date, 
                                     permissions=types.ChatPermissions(can_send_messages=False))
            bot.send_message(message.chat.id, f"🙊 {mention_target} Silencio afsuni ostida! {mute_time} daqiqaga ovozi o'chirildi.\n📜 Sabab: {reason}")
            
        elif cmd == "/unmute":
            bot.restrict_chat_member(message.chat.id, target.id, 
                                     permissions=types.ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
            bot.send_message(message.chat.id, f"🔊 {mention_target}dan afsun yechildi.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xato: {str(e)}")

# --- START VA TEKSHIRISH ---
@bot.message_handler(commands=["start"])
def start_cmd(message):
    user = message.from_user
    
    if message.chat.type != 'private':
        bot_info = bot.get_me()
        btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🏰 Shaxsiy chatga o'tish", url=f"https://t.me/{bot_info.username}?start=start")
        )
        txt = (
            f"Hurmatli yosh sehrgar {get_mention(user)}! ⚡️\n\n"
            "Sehrli menyulardan foydalanish uchun men bilan <b>shaxsiy chatda</b> suhbatlashishingizni so'rayman. "
            "Guruhda xalaqit bermaslik uchun menyularni shu yerda ochamiz! 🤫"
        )
        return bot.reply_to(message, txt, reply_markup=btn)

    banned = load_data(BANNED_FILE)
    if str(user.id) in str(banned):
        return bot.send_message(message.chat.id, "Siz Azkabandagi mahbus kabi botdan chetlatilgansiz! ⛓")

    users = load_data(USERS_FILE)
    if str(user.id) not in users:
        users[str(user.id)] = user.first_name
        save_data(USERS_FILE, users)

    is_subscribed = check_sub(user.id)
    if not is_subscribed:
        btn = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{CHANNEL[1:]}"),
            types.InlineKeyboardButton("👥 Guruh", url=f"https://t.me/{GROUP[1:]}"),
            types.InlineKeyboardButton("✅ Tekshirish", callback_data="recheck_sub")
        )
        txt = f"Xush kelibsan, yosh sehrgar {get_mention(user)}! ⚡️\n\nHogwarts darvozalari ochilishi uchun avval quyidagi manzillarda ro'yxatdan o'tishingiz (a'zo bo'lishingiz) kerak. Aks holda, Platforma 9 ¾ ga kira olmaysiz!"
        return bot.send_message(message.chat.id, txt, reply_markup=btn)
    
    welcome_txt = (
        f"Salom, {get_mention(user)}! Hogwartsga xush kelibsiz! ✨\n\n"
        "Men sizga sehrli kitoblar va kinolarni topishda yordam beraman. "
        "Agar hali fakultetingizni bilmasangiz, Saralovchi shlyapa xizmatingizga tayyor! 🎩"
    )
    bot.send_message(message.chat.id, welcome_txt, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data == "recheck_sub")
def recheck_callback(callback):
    is_subscribed = check_sub(callback.from_user.id)
    if is_subscribed:
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        welcome_txt = f"Ajoyib! Sehrli olam eshiklari siz uchun ochiq, {get_mention(callback.from_user)}! ✨"
        bot.send_message(callback.message.chat.id, welcome_txt, reply_markup=main_menu())
    else:
        bot.answer_callback_query(callback.id, "Siz hali ham bajaran barcha shartlarni bajarmadingiz! Shoshiling, poyezd yo'lga tushmoqda! 🚂", show_alert=True)

# --- ADMIN FUNKSIYALARI ---
@bot.message_handler(commands=["getid"])
def get_file_id(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Menga istalgan fayl (rasm, video, mp3...) yuboring, men sizga uning FILE_ID sini beraman:")
    ADMIN_STATES[message.from_user.id] = "waiting_for_file"

@bot.message_handler(commands=["setwelcome"])
def set_welcome_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Guruh uchun yangi kutib olish matnini yuboring:\n(Ism uchun {name} dan foydaning)")
    ADMIN_STATES[message.from_user.id] = {"state": "waiting_for_welcome_text"}

@bot.message_handler(commands=["admins"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    txt = ("🧙‍♂️ <b>Admin Panel:</b>\n\n/send - Reklama\n/getid - Fayl ID olish\n/setwelcome - Guruhni sozlash\n/ban [ID] - Botdan bloklash")
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=["send"])
def ad_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Reklama xabarini yuboring:")
    ADMIN_STATES[message.from_user.id] = "waiting_for_ad"

# --- MATNLAR VA MULTIMEDIA ISHLOVCHI ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_admin_and_text_replies(message):
    uid = message.from_user.id
    text = message.text

    if uid == ADMIN_ID and uid in ADMIN_STATES:
        state_data = ADMIN_STATES[uid]
        
        if state_data == "waiting_for_file":
            f_id = None
            if message.photo: f_id = message.photo[-1].file_id
            elif message.video: f_id = message.video.file_id
            elif message.document: f_id = message.document.file_id
            elif message.audio: f_id = message.audio.file_id
            elif message.voice: f_id = message.voice.file_id
            
            if f_id: bot.send_message(message.chat.id, f"<code>{f_id}</code>")
            else: bot.send_message(message.chat.id, "Fayl topilmadi.")
            ADMIN_STATES.pop(uid, None)
            return

        elif state_data == "waiting_for_ad":
            users = load_data(USERS_FILE)
            count = 0
            for u in users:
                try:
                    bot.copy_message(u, message.chat.id, message.message_id)
                    count += 1
                except: pass
            bot.send_message(message.chat.id, f"✅ Xabar {count} kishiga yuborildi.")
            ADMIN_STATES.pop(uid, None)
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_text":
            if message.text:
                ADMIN_STATES[uid] = {"state": "waiting_for_welcome_media", "txt": message.text}
                bot.reply_to(message, "Endi kutib olish uchun media (rasm yoki video) yuboring, yoki 'yo'q' deb yozing:")
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_media":
            welcome_db = load_data(WELCOME_FILE)
            cid = str(message.chat.id)
            f_id, f_type = None, "text"
            
            if message.photo: f_id, f_type = message.photo[-1].file_id, "photo"
            elif message.video: f_id, f_type = message.video.file_id, "video"

            welcome_db[cid] = {"text": state_data['txt'], "f_id": f_id, "f_type": f_type}
            save_data(WELCOME_FILE, welcome_db)
            bot.send_message(message.chat.id, "✅ Guruh uchun kutib olish sozlandi!")
            ADMIN_STATES.pop(uid, None)
            return

    if text == "📚 Kitoblar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("📚 Hammasi birda (1-7)", callback_data="get_all_books"),
            types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="b_uz"),
            types.InlineKeyboardButton("🇬🇧 Inglizcha", callback_data="b_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Kitoblar bo'limini tanlang:", reply_markup=btn)
        
    elif text == "🎬 Kinolar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="m_uz"),
            types.InlineKeyboardButton("🇷🇺 Ruscha", callback_data="m_ru"),
            types.InlineKeyboardButton("🇬🇧 Inglizcha", callback_data="m_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Kinolar tilini tanlang:", reply_markup=btn)

    elif text == "🎩 Saralovchi shlyapa":
        uid_str = str(message.from_user.id)
        data = load_data(HOUSES_FILE)
        if uid_str not in data:
            data[uid_str] = random.choice(list(HOUSES_DETAILS.keys()))
            save_data(HOUSES_FILE, data)
        
        h = HOUSES_DETAILS[data[uid_str]]
        msg = bot.send_message(message.chat.id, "🧐 <b>O'ylayapman...</b>")
        time.sleep(2)
        
        final_text = (
            f"{h['txt']}\n\n✨ <b>Hamma narsa ayon!</b> ✨\n\n"
            f"Fakultetingiz: {h['emoji']} <b>{data[uid_str]}</b>\n"
            f"🔑 Kalit so'z: <code>{h['kalit']}</code>\n\n"
            f"Kalit so'zni shlyapaga yuboring 👇"
        )
        shlyapa_btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🎩 Shlyapaga borish", url=f"https://t.me/{SHLYAPA_USER}")
        )
        bot.edit_message_text(final_text, message.chat.id, msg.message_id, reply_markup=shlyapa_btn)

# --- WELCOME (YANGI AZOLAR KELGANDA) ---
@bot.message_handler(content_types=['new_chat_members'])
def on_new_member(message):
    data = load_data(WELCOME_FILE)
    cid = str(message.chat.id)
    bot_info = bot.get_me()
    
    btn = types.InlineKeyboardMarkup(row_width=2).add(
        types.InlineKeyboardButton("📢 Kanalimiz", url=f"https://t.me/{CHANNEL[1:]}"),
        types.InlineKeyboardButton("🎩 Fakultet tanlash", url=f"https://t.me/{bot_info.username}?start=sorting")
    )
    
    for user in message.new_chat_members:
        mention = get_mention(user)
        if cid in data:
            conf = data[cid]
            cap = conf['text'].replace("{name}", mention)
            if conf['f_type'] == "photo": 
                m = bot.send_photo(cid, conf['f_id'], caption=cap, reply_markup=btn)
            elif conf['f_type'] == "video": 
                m = bot.send_video(cid, conf['f_id'], caption=cap, reply_markup=btn)
            else: 
                m = bot.send_message(cid, cap, reply_markup=btn)
            
            Thread(target=delete_after_delay, args=(message.chat.id, m.message_id, 600)).start()

# --- CALLBACK TUGMALARIGA ISHLOV BERISH ---
@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(callback):
    d = callback.data
    
    if d == "get_all_books":
        bot.send_document(callback.message.chat.id, ALL_IN_ONE_BOOK["file_id"], caption=ALL_IN_ONE_BOOK["caption"])
        bot.answer_callback_query(callback.id)
        return
        
    if d == "home":
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        bot.send_message(callback.message.chat.id, "Asosiy menyu:", reply_markup=main_menu())
        return
    
    if d in ["b_uz", "b_en", "m_uz", "m_ru", "m_en"]:
        btn = types.InlineKeyboardMarkup(row_width=1)
        if d == "b_uz":
            for i, b in enumerate(BOOKS_UZ): btn.add(types.InlineKeyboardButton(b["name"], callback_data=f"get_buz_{i}"))
        elif d == "b_en":
            for i, b in enumerate(BOOKS_EN): btn.add(types.InlineKeyboardButton(b["name"], callback_data=f"get_ben_{i}"))
        elif d == "m_uz":
            for i, m in enumerate(MOVIES_UZ): btn.add(types.InlineKeyboardButton(m["name"], callback_data=f"get_muz_{i}"))
        elif d == "m_ru":
            for i, m in enumerate(MOVIES_RU): btn.add(types.InlineKeyboardButton(m["name"], callback_data=f"get_mru_{i}"))
        elif d == "m_en":
            for i, m in enumerate(MOVIES_EN): btn.add(types.InlineKeyboardButton(m["name"], callback_data=f"get_men_{i}"))
        
        btn.add(types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home"))
        bot.edit_message_text("Marhamat, tanlang:", chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=btn)
        return

    if d.startswith("get_"):
        _, code, idx = d.split("_")
        idx = int(idx)
        
        if code == "buz": item = BOOKS_UZ[idx]; f = bot.send_document
        elif code == "ben": item = BOOKS_EN[idx]; f = bot.send_document
        elif code == "muz": item = MOVIES_UZ[idx]; f = bot.send_video
        elif code == "mru": item = MOVIES_RU[idx]; f = bot.send_video
        elif code == "men": item = MOVIES_EN[idx]; f = bot.send_video
        
        f(callback.message.chat.id, item["file_id"], caption=item["caption"])
        bot.answer_callback_query(callback.id)

# --- RENDER PORTINI TINGLOVCHI FLASK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Hogwarts Bot muvaffaqiyatli ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- O'Z-O'ZINI UYG'OTISH (SELF-PING) TIZIMI ---
def keep_alive():
    """Bot uxlab qolmasligi uchun har 10 daqiqada Render URL manziliga signal yuboradi"""
    time.sleep(20) # Bot to'liq yurgizilib olinishi uchun ozgina kutadi
    logging.info("O'z-o'zini uyg'otish tizimi ishga tushdi.")
    while True:
        try:
            response = requests.get(RENDER_URL)
            logging.info(f"⚡️ Uyg'otish signali muvaffaqiyatli yuborildi: {response.status_code}")
        except Exception as e:
            logging.error(f"⚠️ Uyg'otishda xatolik yuz berdi: {e}")
        
        # 10 daqiqa (600 soniya) kutib, keyin yana qayta signal yuboradi
        time.sleep(600)

if __name__ == '__main__':
    # 1. Flask serverni parallel fonda ochamiz
    t_flask = Thread(target=run_flask, daemon=True)
    t_flask.start()
    
    # 2. O'z-o'zini uyg'otuvchi (Self-Ping) tizimini parallel fonda yurgizamiz
    t_ping = Thread(target=keep_alive, daemon=True)
    t_ping
