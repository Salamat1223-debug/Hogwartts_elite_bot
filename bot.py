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
ALL_IN_ONE_BOOK = {"name": "📚 Hammasi birda (1-7)", "file_id": "BQACAgIAAxkBAAIB62oRVNrnQW9Ia4hRFfc7SWea-3qyAAI0HwACIynpS2_wVwpElnx4OwQ", "caption": "📚 Garri Potter: Barcha qismlar (1-7) bitta faylda!\n\n📢 Kanal: @harry_potter_fans_uz"}

BOOKS_UZ = [
    {"name": "📖 1. Falsafiy tosh", "file_id": "BQACAgIAAxkBAAIBqWoRUqQY_NliQTvcdJcf-X222euyAAJwAANL32FJoV4VINX1v7w7BA", "caption": "📖 Nomi: Garri Potter va Falsafiy tosh\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 2. Maxfiy xujra", "file_id": "BQACAgIAAxkBAAIBq2oRUtH21K1BjiNCFoYBoVu9W6LdAAIuAAMErBBKPIghdvjcQUg7BA", "caption": "📖 Nomi: Garri Potter va Maxfiy hujra\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 3. Azkaban maxbusi", "file_id": "BQACAgIAAxkBAAIBsmoRUvp3ooFPNPwuPO5v1uXniet7AAIJBwACX2XYSF0_unn5ZMT9OwQ", "caption": "📖 Nomi: Garri Potter va Azkaban mahbusi\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 4. Otashli jom", "file_id": "BQACAgIAAxkBAAIBtWoRUxTHFhlbO3Z9eh9P1bHSO9DhAAIzAAMErBBKDrJ0tSipFoU7BA", "caption": "📖 Nomi: Garri Potter va Otashli jom\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 5. Kaknus ordeni", "file_id": "BQACAgIAAxkBAAIBu2oRUzgfgclOFlruQWEAAd1JKv5A0QACawAD4DsYSjXVNK0oeVNEOwQ", "caption": "📖 Nomi: Garri Potter va Kaknus ordeni\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 6. Chalazot shaxzoda", "file_id": "BQACAgIAAxkBAAIBv2oRU1OEQXntBJ8sOpiGb8l6A96zAAKSAAM13FBKWt0iBlhIko87BA", "caption": "📖 Nomi: Garri Potter va Chalazot shahzoda\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 7. Ajal tuhfalari", "file_id": "BQACAgIAAxkBAAIBw2oRU3tkny5OW_WxgxAngpJTpQNlAAIPAgACqQiAScSjhssieqeGOwQ", "caption": "📖 Nomi: Garri Potter va Ajal tuhfalari 1\n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 8. La'natlangan bola 1", "file_id": "BQACAgEAAxkBAAIBx2oRU5M0kYcsYOV0bXoULI6TfLxlAALqAANhXKhHFb7cEYG5GhY7BA", "caption": "📖 Nomi: Garri Potter va Laʼnatlangan bola 1 \n\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "📖 9. La'natlangan bola 2", "file_id": "BQACAgIAAxkBAAIBy2oRU68QKtkgr6LbrF22YFDztGkUAAKsAgACLVkpSE4lomSdnwX3OwQ", "caption": "📖 Nomi: Garri Potter va Laʼnatlangan bola 2 \n\n📢 Kanal: @harry_potter_fans_uz"},
]

BOOKS_EN = [
    {"name": "📖 1. Philosopher's Stone", "file_id": "BQACAgUAAxkBAAIBz2oRU97h6-l9CZzNjiFBJYamK_VhAAL_AwACn_N4VXgGRR7hsLnGOwQ", "caption": "📖 Name: Harry Potter 1\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 2. Chamber of Secrets", "file_id": "BQACAgUAAxkBAAIB02oRVAxDTcwqrelfvKChE9iA9rwxAAMEAAKf83hV-8TVNxJyojc7BA", "caption": "📖 Name: Harry Potter 2\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 3. Prisoner of Azkaban", "file_id": "BQACAgUAAxkBAAIB12oRVDtpTFE7bapEXvc_-QABEyxwPAAC_gMAAp_zeFULouFfIzKxxDsE", "caption": "📖 Name: Harry Potter 3\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 4. Goblet of Fire", "file_id": "BQACAgUAAxkBAAIB22oRVFgd1OfBD2KWEVmfTyOG06ueAAL7AwACn_N4VXDNYCGzMToZOwQ", "caption": "📖 Name: Harry Potter 4\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 5. Order of the Phoenix", "file_id": "BQACAgUAAxkBAAIB32oRVHrOWJpcYW9kkIIQuiVbPotoAAL5AwACn_N4VV8bZ_YVl1YlOwQ", "caption": "📖 Name: Harry Potter 5\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 6. Half-Blood Prince", "file_id": "BQACAgUAAxkBAAIB42oRVJWDLWAYhFq5LyZ1VaOuq7itAAL6AwACn_N4VSe_lTxN3QwiOwQ", "caption": "📖 Name: Harry Potter 6\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "ZG 1", "file_id": "BQACAgUAAxkBAAIB52oRVLXkGfqnn5fnHY79CrgGkbGUAAL8AwACn_N4VeoCegxrYS2ZOwQ", "caption": "📖 Name: Harry Potter 7\n📢 Channel: @harry_potter_fans_uz"},
]

MOVIES_UZ = [
    {"name": "🎬 1. Hikmatlar toshi", "file_id": "BAACAgIAAxkBAAIB72oRVVJb-Cq4f8DrzEjeV2VmxBQIAAK9jgACiCDoSvO7NrvjzBUzOwQ", "caption": "🎬 Nomi: HP 1: Hikmatlar toshi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 2. Maxfiy hujra", "file_id": "BAACAgIAAxkBAAIB82oRVXWA-Di59gcb9hMtS4xgFfN0AAOFAALhnOhKSFYAARo3Wz7jOwQ", "caption": "🎬 Nomi: HP 2: Maxfiy hujra\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 3. Azkoban maxbusi", "file_id": "BAACAgIAAxkBAAIB92oRVZaGoO7SrsqIL9d2cdZeNaiyAAJHhQAC4ZzoSiDUtfwcYLPbOwQ", "caption": "🎬 Nomi: HP 3: Azkoban maxbusi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 4. Alanga kubogi", "file_id": "BAACAgIAAxkBAAIB-2oRVeI2CQQm9kt5CEzfDu807b24AAJkhQAC4ZzoShNFpHjnwSQBOwQ", "caption": "🎬 Nomi: HP 4: Alanga kubogi\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 5. Feniks jamiyati", "file_id": "BAACAgIAAxkBAAIB_2oRVgSHV-4oUcRT1_gNUyv3E1UwAAJ-hQAC4ZzoSl0ICI8CDO2IOwQ", "caption": "🎬 Nomi: HP 5: Feniks jamiyati\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 6. Tilsim Shahzoda", "file_id": "BAACAgIAAxkBAAICA2oRVh89fjymNaut7gZte_ncnAI2AAKMhQAC4ZzoSmvMFEOjbqO_OwQ", "caption": "🎬 Nomi: HP 6: Tilsim Shahzoda\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 7. Ajal tuhfasi 1", "file_id": "BAACAgIAAxkBAAICB2oRVjvNjsJ7ulr_I_t1S7C0oxG4AAKXhQAC4ZzoSsPp3Im56dRAOwQ", "caption": "🎬 Nomi: HP 7: Ajal tuhfasi 1\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
    {"name": "🎬 8. Ajal tuhfasi 2", "file_id": "BAACAgIAAxkBAAIB92oRVZaGoO7SrsqIL9d2cdZeNaiyAAJHhQAC4ZzoSiDUtfwcYLPbOwQ", "caption": "🎬 Nomi: HP 8: Ajal tuhfasi 2\n⏱ Vaqti: 2.5 soat\n🌐 Tili: O'zbekcha\n🎞 Sifati: HD\n📢 Kanal: @harry_potter_fans_uz"},
]

MOVIES_RU = [
    {"name": "🎬 1. Философский камень", "file_id": "BAACAgIAAxkBAAICD2oRVoVgqczt0zh2ZLvb0WSxJlktAAIoCgACMf9ZS0p7sgsK2RVBOwQ", "caption": "🎬 Название: ГП 1: Философский камень\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 2. Тайная комната", "file_id": "BAACAgIAAxkBAAICE2oRVqhWj-EE5I4qJ_ZNHsM3FGL7AAImCgACMf9ZSzgm9-awc9oUOwQ", "caption": "🎬 Название: ГП 2: Тайная комната\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 3. Узник Азкабана", "file_id": "BAACAgIAAxkBAAICF2oRVsY83X5ynrcgTqvHXFE83TVwAAInCgACMf9ZS-gYbIiUq-JnOwQ", "caption": "🎬 Название: ГП 3: Узник Азкабана\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 4. Кубок огня", "file_id": "BAACAgIAAxkBAAICG2oRVuKS1Tf-ZuwSjckC7oVKKM_bAAIjCgACMf9ZSwVaW6AlXUfEOwQ", "caption": "🎬 Название: ГП 4: Кубок огня\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 5. Орден Феникса", "file_id": "BAACAgQAAxkBAAICH2oRVwUjorH6X-Rv4T83YsPefwOwAAKgDAAC2L_JUNzUWrpxRUZwOwQ", "caption": "🎬 Название: ГП 5: Орден Феникса\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 6. Принц-полукровка (Bo'sh)", "file_id": "", "caption": "🎬 Bu qism tez orada yuklanadi!"},
    {"name": "🎬 7. Дары Смерти 1", "file_id": "BAACAgIAAxkBAAICI2oRV0Wx7NzLbFCmdF9X7FaqQNt8AALpBAACKP2pSFrR0uVnCfS6OwQ", "caption": "🎬 Название: ГП 7: Дары Смерти 1\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 8. Дары Смерти 2", "file_id": "BAACAgIAAxkBAAICJ2oRV2_mYMkoFScyVooRi-_syltzAAJlBAACxKyhSBZmb1Bk9El8OwQ", "caption": "🎬 Название: ГП 8: Дары Смерти 2\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
]

MOVIES_EN = [
    {"name": "🎬 1. Sorcerer's Stone", "file_id": "BAACAgQAAxkBAAICK2oRV57yz26n0lzTglnUOlgNzn31AAJ_BwACrMaBUL_EFWDu3fSNOwQ", "caption": "🎬 Name: HP 1: Sorcerer's Stone\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 2. Chamber of Secrets", "file_id": "BAACAgQAAxkBAAICL2oRV_ppWrRqkoMAAXc1Lw34961RUgACgQcAAqzGgVBdOFD_iBwOLDsE", "caption": "🎬 Name: HP 2: Chamber of Secrets\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 3. Prisoner of Azkaban", "file_id": "BAACAgQAAxkBAAICM2oRWZxfAAHXBWP0o5kRBMycCICq9QAChwcAAqzGgVDsBQVT8TAICDsE", "caption": "🎬 Name: HP 3: Prisoner of Azkaban\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 4. Goblet of Fire", "file_id": "BAACAgQAAxkBAAICN2oRWbarnoIsnvM0XIlTrvR_owfbAAKOBwACrMaBUDUXSbQwD0IDOwQ", "caption": "🎬 Name: HP 4: Goblet of Fire\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 5. Order of the Phoenix", "file_id": "BAACAgQAAxkBAAICO2oRWcx9S0pQRS4ErbXGwkcCdZfNAAKVBwACrMaBUFprpknOUtC1OwQ", "caption": "🎬 Name: HP 5: Order of the Phoenix\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 6. Half-Blood Prince", "file_id": "BAACAgQAAxkBAAICP2oRWeSo58vRcf6VLnbTaHYcsMmqAAKNCAACqwKBUGyOaaeviG0COwQ", "caption": "🎬 Name: HP 6: Half-Blood Prince\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 7. Deathly Hallows 1", "file_id": "BAACAgQAAxkBAAICQ2oRWfs9uFR8DUVxXjpUNjN64qScAAKXCAACqwKBUMZ1LdCSfm44OwQ", "caption": "🎬 Name: HP 7: Deathly Hallows 1\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 8. Deathly Hallows 2", "file_id": "BAACAgQAAxkBAAICR2oRWhMkyoYUeG5OdS6Dh_bvObG9AAKkCAACqwKBUGsuMQMa_91TOwQ", "caption": "🎬 Name: HP 8: Deathly Hallows 2\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
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

# --- JAZO TIZIMI (HOGWARTS SEHRLI AFSUNLARI) ---
@bot.message_handler(commands=["silencio", "avadakedavra", "finite", "revive"])
def handle_punishment(message):
    sender = message.from_user
    mention_sender = get_mention(sender)
    cmd = message.text.split()[0].lower()

    # Shaxsiy chatda faqat asosiy admin (Jodu Vaziri) ishlata oladi
    if message.chat.type == 'private' and sender.id == ADMIN_ID:
        args = message.text.replace(message.text.split()[0], "").strip()
        if cmd == "/avadakedavra" and args:
            banned = load_data(BANNED_FILE)
            if not isinstance(banned, list): banned = []
            banned.append(args)
            save_data(BANNED_FILE, list(set(banned)))
            return bot.reply_to(message, f"🚫 <code>{args}</code> ID'li shaxs qora sehrgarlikda ayblanib, Avada Kedavra jodusi bilan botdan butunlay yo'q qilindi!")
        elif cmd == "/revive" and args:
            banned = load_data(BANNED_FILE)
            if args in banned:
                banned.remove(args)
                save_data(BANNED_FILE, banned)
                return bot.reply_to(message, f"🕊 <code>{args}</code> tiriltirildi (Revive) va unga botdan qayta foydalanishga ruxsat berildi!")

    if message.chat.type == 'private': return
    
    # Guruhda buyruq bergan odam admin/moderatorligini tekshirish
    try:
        sender_member = bot.get_chat_member(message.chat.id, sender.id)
        is_admin = sender_member.status in ['administrator', 'creator']
    except:
        is_admin = False
    
    if not is_admin:
        return bot.reply_to(message, f"🧙‍♂️ Kechirasiz {mention_sender}, siz hali oddiy o'quvchisiz! Bunday oliy darajali sehrlarni faqat professorlar ishlata oladi! 🪄")

    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Afsun kuchga kirishi uchun uni biror sehrgarning xabariga (Reply) qaratishingiz kerak!")

    target = message.reply_to_message.from_user
    mention_target = get_mention(target)
    
    # 🔴 ASOSIY ADMIN IMMUNITETI (SEHR ORQAGA QAYTADI)
    if target.id == ADMIN_ID:
        return bot.reply_to(
            message, 
            f"🛡 <b>PROTEGO HORRIBILIS!</b> \n\n{mention_sender}, siz hozirgina Jodu Vaziriga qarshi afsun ishlatishga urindingiz! "
            f"Sizning afsuningiz vazirlikning qadimiy himoya qalqoniga urilib, o'zingizga qaytdi! ⚡️"
        )

    try:
        target_member = bot.get_chat_member(message.chat.id, target.id)
        is_target_admin = target_member.status in ['administrator', 'creator']
    except:
        is_target_admin = False
        
    bot_obj = bot.get_me()

    if is_target_admin or target.id == bot_obj.id:
        return bot.reply_to(message, f"🧙‍♂️ {mention_sender}, boshqa bir professor yoki prefektga qarshi duel e'lon qilish taqiqlangan! Hogwarts nizomiga amal qiling.")

    args = message.text.split()[1:]
    
    try:
        # --- AVADA KEDAVRA (BAN) ---
        if cmd == "/avadakedavra":
            bot.ban_chat_member(message.chat.id, target.id)
            bot.send_message(message.chat.id, f"⚡️ <b>AVADA KEDAVRA!</b> \n\n{mention_target} yashil nur ichida g'oyib bo'ldi va Hogwarts guruhidan butunlay haydaldi! ⛓")
        
        # --- REVIVE (UNBAN) ---
        elif cmd == "/revive":
            bot.unban_chat_member(message.chat.id, target.id)
            bot.send_message(message.chat.id, f"🕊 <b>REVIVE!</b> \n\n{mention_target} qayta tiriltirildi va guruh darvozalari unga yana ochildi!")

        # --- SILENCIO (MUTE) ---
        elif cmd == "/silencio":
            mute_time = 5
            reason = "Tartibni buzish"
            
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
            bot.send_message(message.chat.id, f"🙊 <b>SILENCIO!</b> \n\n{mention_target} ovoz o'chirish afsuni ostida qoldi! U {mute_time} daqiqa davomida guruhda gapira olmaydi.\n📜 Sabab: {reason}")
            
        # --- FINITE (UNMUTE) ---
        elif cmd == "/finite":
            bot.restrict_chat_member(message.chat.id, target.id, 
                                     permissions=types.ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
            bot.send_message(message.chat.id, f"🔊 <b>FINITE INCANTATEM!</b> \n\n{mention_target} ustidagi afsun yechildi. Shovqin solmasdan gapirishi mumkin.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Afsun amalga oshmadi, xatolik: {str(e)}")

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
            f"Hurmatli yosh sehrgar {get_mention(user)}! ⚡\n\n"
            "Sehrli menyulardan foydalanish uchun men bilan <b>shaxsiy chatda</b> suhbatlashishingizni so'rayman. "
            "Katta Zalda shovqin ko'tarmaslik uchun shaxsiy xonaga o'tamiz! 🤫"
        )
        return bot.reply_to(message, txt, reply_markup=btn)

    banned = load_data(BANNED_FILE)
    if str(user.id) in str(banned):
        return bot.send_message(message.chat.id, "Siz Azkabandagi mahbus kabi botdan chetlatilgansiz! Dementorlar yaqinlashmoqda... ⛓")

    users = load_data(USERS_FILE)
    if str(user.id) not in users:
        users[str(user.id)] = user.first_name
        save_data(USERS_FILE, users)

    is_subscribed = check_sub(user.id)
    if not is_subscribed:
        btn = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("📢 Vazirlik Kanali", url=f"https://t.me/{CHANNEL[1:]}"),
            types.InlineKeyboardButton("👥 Hogwarts Guruhi", url=f"https://t.me/{GROUP[1:]}"),
            types.InlineKeyboardButton("✅ Aloqani tekshirish", callback_data="recheck_sub")
        )
        txt = f"Xush kelibsan, yosh sehrgar {get_mention(user)}! ⚡\n\nHogwarts darvozalari ochilishi uchun avval quyidagi guruh va kanalda qayddan o'tishingiz kerak. Aks holda, Platforma 9 ¾ ga kira olmaysiz va poyezd ketib qoladi! 🚂"
        return bot.send_message(message.chat.id, txt, reply_markup=btn)
    
    welcome_txt = (
        f"Salom, {get_mention(user)}! Hogwartsga xush kelibsiz! ✨\n\n"
        "Men sizga eng nodir sehrli kitoblar va kinolarni topishda yordam beraman. "
        "Agar hali qaysi fakultetda o'qishingizni bilmasangiz, Saralovchi shlyapa buyrug'ingizga muntazir! 🎩"
    )
    bot.send_message(message.chat.id, welcome_txt, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data == "recheck_sub")
def recheck_callback(callback):
    is_subscribed = check_sub(callback.from_user.id)
    if is_subscribed:
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        welcome_txt = f"Ajoyib! Sehrli olam eshiklari siz uchun ochildi, marhamat {get_mention(callback.from_user)}! ✨"
        bot.send_message(callback.message.chat.id, welcome_txt, reply_markup=main_menu())
    else:
        bot.answer_callback_query(callback.id, "Siz hali ham barcha shartlarni bajarmadingiz! Shoshiling, poyezd yo'lga tushmoqda! 🚂", show_alert=True)

# --- ADMIN FUNKSIYALARI ---
@bot.message_handler(commands=["getid"])
def get_file_id(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Sehrgar xo'jayin, menga istalgan artefaktni (fayl) yuboring, men uning yashirin kodini (FILE_ID) o'qib beraman:")
    ADMIN_STATES[message.from_user.id] = "waiting_for_file"

@bot.message_handler(commands=["setwelcome"])
def set_welcome_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Katta Zalda yangi talabalarni kutib olish uchun xabarnoma yuboring (Ism o'rniga {name} yozing):")
    ADMIN_STATES[message.from_user.id] = {"state": "waiting_for_welcome_text"}

@bot.message_handler(commands=["admins"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    txt = ("🧙‍♂️ <b>Jodu Vaziri Paneli:</b>\n\n/send - Barcha sehrgarlarga bayonot (reklama)\n/getid - Artefakt ID sini olish\n/setwelcome - Kutib olishni sozlash\n/ban [ID] - Botdan butunlay haydash")
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=["send"])
def ad_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Barcha talabalarga yuboriladigan sehrli xabarni kiriting:")
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
            else: bot.send_message(message.chat.id, "Artefakt ichida kod topilmadi.")
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
            bot.send_message(message.chat.id, f"✅ Sehrli bayonot {count} ta sehrgarga yetkazildi.")
            ADMIN_STATES.pop(uid, None)
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_text":
            if message.text:
                ADMIN_STATES[uid] = {"state": "waiting_for_welcome_media", "txt": message.text}
                bot.reply_to(message, "Ajoyib! Endi kutib olish vizual ko'rinishi uchun media (rasm yoki video) yuboring yoki 'yo'q' deb yozing:")
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_media":
            welcome_db = load_data(WELCOME_FILE)
            cid = str(message.chat.id)
            f_id, f_type = None, "text"
            
            if message.photo: f_id, f_type = message.photo[-1].file_id, "photo"
            elif message.video: f_id, f_type = message.video.file_id, "video"

            welcome_db[cid] = {"text": state_data['txt'], "f_id": f_id, "f_type": f_type}
            save_data(WELCOME_FILE, welcome_db)
            bot.send_message(message.chat.id, "✅ Katta Zal uchun yangi talabalarni kutib olish tizimi sozlandi!")
            ADMIN_STATES.pop(uid, None)
            return

    if text == "📚 Kitoblar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("📚 Hammasi birda (1-7)", callback_data="get_all_books"),
            types.InlineKeyboardButton("🇺🇿 O'zbekcha tarjima", callback_data="b_uz"),
            types.InlineKeyboardButton("🇬🇧 Original inglizcha", callback_data="b_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Flurish va Blotts kitob do'koniga xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=btn)
        
    elif text == "🎬 Kinolar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="m_uz"),
            types.InlineKeyboardButton("🇷🇺 Ruscha", callback_data="m_ru"),
            types.InlineKeyboardButton("🇬🇧 Inglizcha", callback_data="m_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Sehrli kinotasvirlar bo'limi. Tilni tanlang:", reply_markup=btn)

    elif text == "🎩 Saralovchi shlyapa":
        uid_str = str(message.from_user.id)
        data = load_data(HOUSES_FILE)
        if uid_str not in data:
            data[uid_str] = random.choice(list(HOUSES_DETAILS.keys()))
            save_data(HOUSES_FILE, data)
        
        h = HOUSES_DETAILS[data[uid_str]]
        msg = bot.send_message(message.chat.id, "🧐 <b>Shlyapa ko'zlaringizga tikilib o'ylamoqda...</b>")
        time.sleep(2)
        
        final_text = (
            f"{h['txt']}\n\n✨ <b>Hamma narsa ayon!</b> ✨\n\n"
            f"Siz munosib bo'lgan fakultet: {h['emoji']} <b>{data[uid_str]}</b>\n"
            f"🔑 Kirish afsuni (kalit so'z): <code>{h['kalit']}</code>\n\n"
            f"Fakultet guruhiga kirish uchun afsun so'zini Shlyapaga yuboring 👇"
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
        types.InlineKeyboardButton("📢 Vazirlik Kanali", url=f"https://t.me/{CHANNEL[1:]}"),
        types.InlineKeyboardButton("🎩 Fakultetni aniqlash", url=f"https://t.me/{bot_info.username}?start=sorting")
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
        bot.send_message(callback.message.chat.id, "Hogwarts asosiy xizmatlari:", reply_markup=main_menu())
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
        bot.edit_message_text("Marhamat, o'zingizga kerakli tom (qism)ni tanlang:", chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=btn)
        return

    if d.startswith("get_"):
        _, code, idx = d.split("_")
        idx = int(idx)
        
        if code == "buz": item = BOOKS_UZ[idx]; f = bot.send_document
        elif code == "ben": item = BOOKS_EN[idx]; f = bot.send_document
        elif code == "muz": item = MOVIES_UZ[idx]; f = bot.send_video
        elif code == "mru": item = MOVIES_RU[idx]; f = bot.send_video
        elif code == "men": item = MOVIES_EN[idx]; f = bot.send_video
        
        if not item["file_id"]:
            bot.send_message(callback.message.chat.id, item["caption"])
        else:
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
    time.sleep(20)
    logging.info("O'z-o'zini uyg'otish tizimi ishga tushdi.")
    while True:
        try:
            response = requests.get(RENDER_URL)
            logging.info(f"⚡️ Uyg'otish signali muvaffaqiyatli yuborildi: {response.status_code}")
        except Exception as e:
            logging.error(f"⚠️ Uyg'otishda xatolik yuz berdi: {e}")
        time.sleep(600)

def run_bot():
    logging.info("Bot polling oqimi alohida ishga tushmoqda...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"Bot pollingda xatolik yuz berdi: {e}")
            time.sleep(5)

if __name__ == '__main__':
    t_bot = Thread(target=run_bot, daemon=True)
    t_bot.start()
    
    t_ping = Thread(target=keep_alive, daemon=True)
    t_ping.start()
    
    logging.info("Flask veb-server asosiy portda ishga tushdi.")
    run_flask()
