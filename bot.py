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
CHANNEL = "@harry_potter_fans_uz"
GROUP = "@hogwarts_elite"
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
    {"name": "📖 5. Order of the Phoenix", "file_id": "BQACAgQAAxkBAAIB32oRVHrOWJpcYW9kkIIQuiVbPotoAAL5AwACn_N4VV8bZ_YVl1YlOwQ", "caption": "📖 Name: Harry Potter 5\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "📖 6. Half-Blood Prince", "file_id": "BQACAgQAAxkBAAIB42oRVJWDLWAYhFq5LyZ1VaOuq7itAAL6AwACn_N4VSe_lTxN3QwiOwQ", "caption": "📖 Name: Harry Potter 6\n📢 Channel: @harry_potter_fans_uz"},
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
    {"name": "🎬 5. Орден Феникса", "file_id": "BAACAgQAAxkBAAICH2oRVwUjorH6X-Rv4T83YsPefwOwAAKgDAAC2L_JUNzUWrpxRUZwOwQ", "caption": "🎬 Название: Орден Феникса\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 6. Принц-полукровка (Bo'sh)", "file_id": "", "caption": "🎬 Bu qism tez orada yuklanadi!"},
    {"name": "🎬 7. Дары Смерти 1", "file_id": "BAACAgIAAxkBAAICI2oRV0Wx7NzLbFCmdF9X7FaqQNt8AALpBAACKP2pSFrR0uVnCfS6OwQ", "caption": "🎬 Название: ГП 7: Дары Смерти 1\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
    {"name": "🎬 8. Дары Смерти 2", "file_id": "BAACAgIAAxkBAAICJ2oRV2_mYMkoFScyVooRi-_syltzAAJlBAACxKyhSBZmb1Bk9El8OwQ", "caption": "🎬 Название: ГП 8: Дары Смерти 2\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
]

MOVIES_EN = [
    {"name": "🎬 1. Sorcerer's Stone", "file_id": "BAACAgQAAxkBAAICK2oRV57yz26n0lzTglnUOlgNzn31AAJ_BwACrMaBUL_EFWDu3fSNOwQ", "caption": "🎬 Name: HP 1: Sorcerer's Stone\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 2. Chamber of Secrets", "file_id": "BAACAgQAAxkBAAICL2oRV_ppWrRqkoMAAXc1Lw34961RUgACgQcAAqzGgVBdOFD_iBwOLDsE", "caption": "🎬 Name: HP 2: Chamber of Secrets\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 3. Prisoner of Azkaban", "file_id": "BAACAgQAAxkBAAICM2oRWZxfAAHXBWP0o5kRBMycCICq9QAChwcAAqzGgVDsBQVT8TAICDsE", "caption": "🎬 Name: HP 3: Prisoner of Azkaban\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 4. Goblet of Fire", "file_id": "BAACAgQAAxkBAAICN2oRWbarnoIsnvM0XIlTrvR_owfbAAKOBwACrMaBUDUXSbQwD0IDOwQ", "caption": "🎬 Name: HP 4: Goblet of Fire\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 5. Order of the Phoenix", "file_id": "BAACAgOAAxkBAAICO2oRWcx9S0pQRS4ErbXGwkcCdZfNAAKVBwACrMaBUFprpknOUtC1OwQ", "caption": "🎬 Name: HP 5: Order of the Phoenix\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 6. Half-Blood Prince", "file_id": "BAACAgQAAxkBAAICP2oRWeSo58vRcf6VLnbTaHYcsMmqAAKNCAACqwKBUGyOaaeviG0COwQ", "caption": "🎬 Name: HP 6: Half-Blood Prince\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 7. Deathly Hallows 1", "file_id": "BAACAgQAAxkBAAICQ2oRWfs9uFR8DUVxXjpUNjN64qScAAKXCAACqwKBUMZ1LdCSfm44OwQ", "caption": "🎬 Name: HP 7: Deathly Hallows 1\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
    {"name": "🎬 8. Deathly Hallows 2", "file_id": "BAACAgQAAxkBAAICR2oRWhMkyoYUeG5OdS6Dh_bvObG9AAKkCAACqwKBUGsuMQMa_91TOwQ", "caption": "🎬 Name: HP 8: Deathly Hallows 2\n⏱ Time: 2.5 hours\n🌐 Lang: English\n🎞 Quality: HD\n📢 Channel: @harry_potter_fans_uz"},
]

HOUSES_DETAILS = {
    "Gryffindor": {"emoji": "🦁", "kalit": "jasorat", "txt": "🦁 <b>Saralovchi Shlyapa pichirlamoqda:</b>\n\n<i>«Yuraging to'la qo'rqmaslik va olijanoblik. Sen xavf-xatarga tik boqishni bilasan, adolat uchun kurashishdan tolgan emassan. Jasurlik sening qoningda, yosh sehrgar!»</i>"},
    "Slytherin": {"emoji": "🐍", "kalit": "ilon", "txt": "🐍 <b>Saralovchi Shlyapa pichirlamoqda:</b>\n\n<i>«Buyuklikka bo'lgan so'nmas intilish... O'tkir makr, g'urur va har qanday vaziyatdan aql bilan chiqib keta olish munosabati. Sen maqsad sari hech narsadan to'xtamaysan, senga buyuk kelajak yarashadi!»</i>"},
    "Ravenclaw": {"emoji": "🦅", "kalit": "burgut", "txt": "🦅 <b>Saralovchi Shlyapa pichirlamoqda:</b>\n\n<i>«O'tkir zehn, donolik va bilimga bo'lgan cheksiz chanqoqlik. Sening noodatiy fikrlashing va zukkoliging har qanday qiyin jumboqni osongina yechishga qodir. Bilim sening eng qudratli qurolingdir!»</i>"},
    "Hufflepuff": {"emoji": "🦡", "kalit": "aql", "txt": "🦡 <b>Saralovchi Shlyapa pichirlamoqda:</b>\n\n<i>«E-eh, men senda eng buyuk fazilatni ko'ryapman... Sadoqat, mehnatsevarlik va tenglik senda birinchi o'rinda. Mehnat qilishdan aslo qo'rqmaysan, do'stlaring va yaqinlaring uchun chin dildan qayg'urasan!»</i>"}
}

# 🔮 SEHRLI ITTIFOQLAR BAZASI (FENIKS JAMIYATI VA AJAL KASOFATLARI)
PROJECT_GROUPS = {
    "Feniks Jamiyati": {
        "emoji": "⚡️",
        "txt": "🕊 <b>ALBUS DUMBLEDORE FARMONI BILAN:</b>\n\nSiz yorug'lik va adolat timsoli bo'lgan <b>Feniks Jamiyati</b> (Order of the Phoenix) safiga munosib ko'rildingiz! ⚡️\nYuragingizdagi ezgulik va yorqin kelajakka bo'lgan ishonch sizni Albus Dumbledore boshchiligidagi buyuk ittifoqqa boshladi. Loyihalarda yorug'lik kuchini ko'rsating!"
    },
    "Ajal Kasofatlari": {
        "emoji": "💀",
        "txt": "🔥 <b>LORD VOLDEMORTNING SEHRLI BUYRUG'I BILAN:</b>\n\nSiz eng qudratli va cheksiz kuchga intiluvchi <b>Ajal Kasofatlari</b> (Death Eaters) ittifoqiga saralandingiz! 💀🔥\nSizning mardligingiz, yashirin makringiz va buyuklikka bo'lgan so'nmas chanqog'ingiz Qora Lord saflarida aks etdi. Eng qiyin topshiriqlar va qudrat endi siz tomonda!"
    }
}

# 🦄 PATRONUS SHAKLLARI BAZASI
PATRONUS_SHAPES = [
    {"animal": "Bug'u (Stag)", "emoji": "🦌", "desc": "Sizning ichki kuchingiz yetakchilik, himoya va cheksiz jasoratga tayanadi. Huddi Jeyms va Garri Potter kabi!"},
    {"animal": "Eshshak kiyik (Doe)", "emoji": "🦌", "desc": "Sizning Patronusingiz toza muhabbat, sadoqat va abadiy g'amxo'rlik timsolidir. Severus Sneyp va Lili Potter kabi."},
    {"animal": "Bo'ri (Wolf)", "emoji": "🐺", "desc": "Siz tabiatingizdan sadoqatli, oilaparvar va ittifoqni qadrlovchi sehrgarsiz. Remus Lyupin kabi."},
    {"animal": "Ot (Horse)", "emoji": "🐎", "desc": "Erkinlik, quvvat va sodda, lekin o'ta qat'iy xarakter egasisiz. Jinni Vizli kabi."},
    {"animal": "Suvsar (Otter)", "emoji": "🦦", "desc": "Zukkolik, qiziquvchanlik va har qanday vaziyatda to'g'ri qaror topa olish qobiliyati. Germiona Greynjer kabi."},
    {"animal": "Feniks qushi (Phoenix)", "emoji": "🦅", "desc": "Eng nodir Patronus! Siz har qanday qiyinchilikdan qayta tug'ila olasiz va qalbingiz o'ta toza. Albus Dumbledore kabi!"},
    {"animal": "Mushuk (Cat)", "emoji": "🐈", "desc": "Kuzatuvchan, ehtiyotkor va qat'iy tartib-intizomni sevuvchi sehrgarsiz. Professor Makgonagall kabi."}
]

# 🧪 MA'JUN TAYYORLASH DARSBOB MATNLARI
POTIONS_LIST = [
    {"name": "Omad Sharbati (Felix Felicis)", "emoji": "🧪✨", "desc": "Oltin rangda tovlanuvchi bu sharbat sizga bugun barcha ishlaringizda mutloq omad keltiradi! 24 soat davomida omad siz tomonda!"},
    {"name": "Amortensiya (Sevgi ma'juni)", "emoji": "🧪💖", "desc": "O'ziga xos marvariddek yaltirashga ega va spiralsimon bug' chiqaruvchi eng qudratli sevgi ma'juni! Ehtiyot bo'ling!"},
    {"name": "Ko'p qiyofali ma'jun (Polyjuice Potion)", "emoji": "🧪🎭", "desc": "Siz ma'junni to'g'ri tayyorladingiz! Endi unga biror sehrgarning sochini qo'shib, 1 soat davomida uning qiyofasiga kirishingiz mumkin."},
    {"name": "Tinchlik malhami (Draught of Peace)", "emoji": "🧪🌀", "desc": "Asabiylik va xavotirni zumda so'ndiruvchi kumushrang mayin sharbat. Imtihonlar oldidan juda foydali."},
    {"name": "Tirik o'lim damlamasi (Draught of Living Death)", "emoji": "🧪💤", "desc": "O'ta qudratli uyqu dori. Ichgan odamni hayot belgilari bilinmaydigan darajada chuqur uyquga ketkazadi."}
]

# --- BAZA FAYLLARI ---
HOUSES_FILE = "user_houses.json"
GROUPS_FILE = "user_project_groups.json"
USERS_FILE = "users_list.json"
WELCOME_FILE = "welcome_settings.json"
BANNED_FILE = "banned_users.json"
PATRONUS_FILE = "user_patronus.json"  # <-- Yangi Patronus bazasi

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
    markup.add(types.KeyboardButton("🎩 Saralovchi shlyapa"), types.KeyboardButton("🌀 Saralash"))
    markup.add(types.KeyboardButton("🦄 Patronus testi"), types.KeyboardButton("🧪 Ma'jun tayyorlash"))
    return markup

def delete_after_delay(chat_id, message_id, delay=600):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# =====================================================================
#  🏰 AZKABAN QOCHQINI O'YINI MANTIQI VA TAKOMILLASHTIRILGAN BAZASI
# =====================================================================
AZKABAN_SESSIONS = {}

def get_game_rules():
    return (
        "📜 <b>Azkaban Qochqini — O'yin Qoidalari</b>\n\n"
        "Guruhda mahbuslarni aniqlash bo'yicha detektiv o'yin! O'yin boshlangach sehrgarlar tugma orqali ro'yxatdan o'tadilar.\n\n"
        "👥 <b>Rollar va Balans:</b>\n"
        "• 3-5 ta sehrgar: 1 ta mahbus | 2 ta fosh etish urinishi\n"
        "• 6-10 ta sehrgar: 2 ta mahbus | 3 ta fosh etish urinishi\n"
        "• 11-20 ta sehrgar: 3 ta mahbus | 4 ta fosh etish urinishi\n"
        "• 21+ ta sehrgar: 4 ta mahbus | 5 ta fosh etish urinishi\n\n"
        "🎯 <b>G'alaba shartlari:</b>\n"
        "1️⃣ <b>Sehrgarlar Vazirligi (Guruh):</b> Qochqinlarni so'zlaridan tahlil qilib, hamma urinishlar tugashidan oldin ularni <code>/revelio</code> afsuni bilan fosh etishi kerak.\n"
        "2️⃣ <b>Azkaban Mahbuslari:</b> Guruh a'zolarini chalg'itib, vazirlik urinishlarini tugatish yoki guruhda yashirincha o'zini bildirmasdan <b>7 ta ma'noli xabar</b> yozish (kamida 3 ta so'zdan iborat).\n\n"
        "🎮 <b>Buyruqlar:</b>\n"
        "• /start_azkaban — O'yinni guruhda boshlash\n"
        "• /extend_azkaban — Ro'yxatdan o'tish vaqtini 30 soniyaga uzaytirish ⏳\n"
        "• /status_azkaban — O'yin holati va ishtirokchilar ro'yxati ✨\n"
        "• /qoidalar — Qoidalarni ko'rmoq\n\n"
        "⏳ <b>Vaqt cheklovi:</b> Vazirlikka mahbuslarni topish uchun jami <b>10 daqiqa</b> vaqt beriladi! Aks holda mahbuslar qochib ketadi!"
    )

@bot.message_handler(commands=["qoidalar"])
def show_azkaban_rules(message):
    bot.reply_to(message, get_game_rules(), parse_mode="HTML")

@bot.message_handler(commands=["status_azkaban"])
def show_game_status(message):
    chat_id = message.chat.id
    if chat_id not in AZKABAN_SESSIONS or AZKABAN_SESSIONS[chat_id]["status"] != "playing":
        return bot.reply_to(message, "❌ Hozirda guruhda faol qidiruv operatsiyasi ketmayapti.")
        
    session = AZKABAN_SESSIONS[chat_id]
    
    txt = "🕵️‍♂️ <b>Azkaban Operatsiyasi — Joriy Holat:</b>\n\n"
    txt += f"🩸 Vazirlik urinishlari: <b>{session['attempts']} ta</b>\n"
    txt += f"👥 Jami qidiruvdagi mahbuslar: <b>{len(session['fugitives'])} ta</b>\n"
    txt += f"RUN 🏃‍♂️ Ko'rinmas bo'lganlar: <b>{len(session['escaped_fugitives'])} ta</b>\n\n"
    
    txt += "🧙‍♂️ <b>Ro'yxatdan o'tgan sehrgarlar:</b>\n"
    for p_id, p_obj in session["players"].items():
        if p_id in session["escaped_fugitives"]:
            txt += f"• {get_mention(p_obj)} — 🏃‍♂️ (Tunda qochib ketdi)\n"
        elif p_id in session["players"] and p_id not in session["fugitives"] and p_id in session["msg_counts"]:
            txt += f"• {get_mention(p_obj)} — ⛓ (Azkabanga qaytarildi)\n"
        else:
            txt += f"• {get_mention(p_obj)} — 👤 (Gumon ostida)\n"
            
    bot.send_message(chat_id, txt, parse_mode="HTML")

# --- VAQTNI UZAYTIRISH BUYRUG'I ---
@bot.message_handler(commands=["extend_azkaban"])
def extend_registration_time(message):
    chat_id = message.chat.id
    try:
        member = bot.get_chat_member(chat_id, message.from_user.id)
        is_admin = member.status in ['administrator', 'creator'] or message.from_user.id == ADMIN_ID
    except:
        is_admin = False

    if not is_admin:
        return bot.reply_to(message, "🧙‍♂️ Kechirasiz, taymer sehrini boshqarish uchun sizda yetarli huquq yo'q!")

    if chat_id not in AZKABAN_SESSIONS or AZKABAN_SESSIONS[chat_id]["status"] != "registration":
        return bot.reply_to(message, "❌ Hozirda ro'yxatdan o'tish jarayoni ketmayapti, vaqtni uzaytirib bo'lmaydi.")

    AZKABAN_SESSIONS[chat_id]["countdown"] += 30
    bot.send_message(chat_id, f"⏳ <b>Afsun kuchi bilan taymer uzaytirildi!</b> \nRo'yxatdan o'tish uchun yana <b>30 soniya</b> qo'shildi!")

@bot.message_handler(commands=["start_azkaban"])
def start_azkaban_game(message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        return bot.reply_to(message, "🏰 Bu o'yinni faqat sehrgarlar guruhida boshlash mumkin!")
    
    if chat_id in AZKABAN_SESSIONS and AZKABAN_SESSIONS[chat_id]["status"] != "ended":
        return bot.reply_to(message, "🕵️‍♂️ Hozirda guruhda Azkaban qidiruv operatsiyasi faol holatda!")

    AZKABAN_SESSIONS[chat_id] = {
        "status": "registration",
        "players": {}, 
        "fugitives": [], 
        "escaped_fugitives": [], 
        "attempts": 2,
        "msg_counts": {},
        "start_time": 0,
        "countdown": 45  
    }

    bot_info = bot.get_me()
    join_url = f"https://t.me/{bot_info.username}?start=join_{chat_id}"
    
    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🧙‍♂️ Safga qo'shilish", url=join_url)
    )
    
    bot.send_message(
        chat_id,
        "🚨 <b>DIQQAT! AZKABANDAN MAHBUSLAR QOCHDI!</b> 🚨\n\n"
        "Sehrgarlar Vazirligi tezkor qidiruv guruhini tuzmoqda. O'yinga qo'shilish va tarkibga kirish uchun quyidagi tugmani bosing.\n"
        "⏳ Ro'yxatdan o'tish uchun 45 soniya vaqt bor! (Adminlar vaqtni /extend_azkaban orqali cho'zishi mumkin)",
        reply_markup=kb,
        parse_mode="HTML"
    )
    
    Thread(target=process_registration_countdown, args=(chat_id,)).start()

def process_registration_countdown(chat_id):
    while True:
        time.sleep(5)
        if chat_id not in AZKABAN_SESSIONS or AZKABAN_SESSIONS[chat_id]["status"] != "registration":
            return
        AZKABAN_SESSIONS[chat_id]["countdown"] -= 5
        if AZKABAN_SESSIONS[chat_id]["countdown"] <= 0:
            break

    session = AZKABAN_SESSIONS[chat_id]
    p_count = len(session["players"])

    if p_count < 3:
        bot.send_message(chat_id, "❌ Qidiruv guruhiga yetarli sehrgar yig'ilmadi (Kamida 3 kishi kerak). Operatsiya bekor qilindi.")
        AZKABAN_SESSIONS.pop(chat_id, None)
        return

    if p_count <= 5:
        f_count, attempts = 1, 2
    elif p_count <= 10:
        f_count, attempts = 2, 3
    elif p_count <= 20:
        f_count, attempts = 3, 4
    else:
        f_count, attempts = 4, 5

    session["attempts"] = attempts
    p_ids = list(session["players"].keys())
    
    chosen_fugitives = random.sample(p_ids, min(f_count, len(p_ids)))
    session["fugitives"] = chosen_fugitives
    session["status"] = "playing"
    session["start_time"] = time.time()

    group_chat = bot.get_chat(chat_id)
    group_link = f"https://t.me/{group_chat.username}" if group_chat.username else "https://t.me/c/" + str(abs(chat_id))[3:]
    
    group_kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("⚔️ Guruhga qaytish (Tergov xonasi)", url=group_link)
    )

    for p_id, p_obj in session["players"].items():
        try:
            if p_id in chosen_fugitives:
                session["msg_counts"][p_id] = 0
                bot.send_message(
                    p_id,  
                    f"👁‍🗨 <b>{p_obj.first_name}</b>, Qora Lord sizga yashirin topshiriq berdi!\n\n"
                    f"Siz <b>Azkaban qochqinisiz!</b> Guruhda o'zingizni aslo bildirmang. "
                    f"Maqsadingiz guruh suhbatiga aralashib, kamida 3 ta so'zdan iborat bo'lgan <b>7 ta xabar</b> yozish "
                    f"yoki Sehrgarlar Vazirligi xodimlarini chalg'itib adashtirish! 🤫",
                    reply_markup=group_kb,
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    p_id,
                    f"🧙‍♂️ <b>{p_obj.first_name}</b>, siz Sehrgarlar Vazirligi tarkibiga qabul qilindingiz!\n\n"
                    f"Sizning vazifangiz — <b>Vazirlik tergovchisisiz!</b> Guruhdagi har bir xabarni diqqat bilan kuzating. "
                    f"Mahbuslarni so'zlaridan tahlil qilib, fosh eting! Adashmang, afsun imkoniyatlari cheklangan. ⚖️",
                    reply_markup=group_kb,
                    parse_mode="HTML"
                )
        except Exception as e:
            logging.error(f"Rol yuborishda xato ({p_id}): {e}")

    participants_list = "\n".join([f"• {get_mention(obj)}" for obj in session["players"].values()])

    bot.send_message(
        chat_id,
        f"🕵️‍♂️ <b>Qidiruv boshlandi! Rollar tarqatildi!</b>\n\n"
        f"📋 <b>Tergovda qatnashayotgan sehrgarlar ro'yxati:</b>\n{participants_list}\n\n"
        f"Guruhda jami {p_count} ta sehrgardan <b>{len(chosen_fugitives)} ta yashirin mahbus</b> bor.\n"
        f"Ularni fosh etish uchun guruhda xabarga javoban (Reply) <code>/revelio</code> yozing.\n\n"
        f"⚠️ Vazirlikda jami <b>{attempts} ta xato qilish</b> imkoniyati bor!\n"
        f"⏳ Mahbuslarni fosh etish uchun sizga <b>10 daqiqa</b> vaqt berildi!",
        parse_mode="HTML"
    )
    
    Thread(target=game_time_limit_timer, args=(chat_id,)).start()

def game_time_limit_timer(chat_id):
    time.sleep(600)
    if chat_id in AZKABAN_SESSIONS and AZKABAN_SESSIONS[chat_id]["status"] == "playing":
        session = AZKABAN_SESSIONS[chat_id]
        all_f_mentions = ", ".join([get_mention(session["players"][f_id]) for f_id in session["fugitives"] if f_id in session["players"]])
        
        bot.send_message(
            chat_id,
            f"⏳ <b>VAQT TUGADI! Operatsiya muvaffaqiyatsiz yakunlandi.</b>\n\n"
            f"Sehrgarlar Vazirligi belgilangan 10 daqiqa ichida mahbuslarni tuta olmadi. "
            f"Haqiqiy qochqinlar: {all_f_mentions} tunda butunlay qochib ketishdi! 💀🔥",
            parse_mode="HTML"
        )
        AZKABAN_SESSIONS.pop(chat_id, None)

# =====================================================================

# --- JAZO TIZIMI (HOGWARTS SEHRLI AFSUNLARI - VAZIRLIK USLUBIDA) ---
@bot.message_handler(commands=["silencio", "avadakedavra", "finite", "revive", "revelio"])
def handle_punishment(message):
    sender = message.from_user
    mention_sender = get_mention(sender)
    cmd = message.text.split()[0].lower()

    if cmd == "/revelio":
        chat_id = message.chat.id
        if message.chat.type == 'private':
            return bot.reply_to(message, "Bu afsunni faqat guruhda ishlatish mumkin!")
        
        if chat_id not in AZKABAN_SESSIONS or AZKABAN_SESSIONS[chat_id]["status"] != "playing":
            return bot.reply_to(message, "Hozirda hech qanday qidiruv o'yini ketmayapti. Boshlash uchun: /start_azkaban")
            
        if not message.reply_to_message:
            return bot.reply_to(message, "⚠️ Afsunni yo'naltirish uchun gumonlanayotgan sehrgarning xabariga (Reply) javob yozing!")

        target = message.reply_to_message.from_user
        session = AZKABAN_SESSIONS[chat_id]

        if target.id not in session["players"]:
            return bot.reply_to(message, "❌ Bu shaxs o'yin ro'yxatidan o'tmagan, u oddiy Hogwarts mehmoni!")

        if target.id in session["escaped_fugitives"]:
            return bot.reply_to(message, "🏃‍♂️ Bu mahbus allaqachon tunda ko'rinmaslik jomshorini kiyib qochib ketgan!")

        if target.id in session["fugitives"]:
            session["fugitives"].remove(target.id)
            session["msg_counts"][target.id] = -1 
            bot.send_message(
                chat_id,
                f"💥 <b>REVELIO!</b> 💥\n\n"
                f"Daxshat! {get_mention(target)} haqiqatdan ham Azkabandan qochgan mahbus bo'lib chiqdi! "
                f"Dementorlar uni o'rab olishdi va qayta zindonga bandi qilishdi. ✨\n"
                f"Guruhda yana <b>{len(session['fugitives'])}</b> ta mahbus yashirinib yuribdi.",
                parse_mode="HTML"
            )
            
            if not session["fugitives"]:
                bot.send_message(chat_id, "🎉 <b>G'ALABA!</b> Sehrgarlar Vazirligi xodimlari barcha mahbuslarni muvaffaqiyatli fosh etdi va Hogwarts xavfsizligini ta'minladi!")
                AZKABAN_SESSIONS.pop(chat_id, None)
        else:
            session["attempts"] -= 1
            if session["attempts"] <= 0:
                all_f_mentions = ", ".join([get_mention(session["players"][f_id]) for f_id in session["fugitives"] if f_id in session["players"]])
                bot.send_message(
                    chat_id,
                    f"💀 <b>Vazirlik mag'lub bo'ldi!</b> 💀\n\n"
                    f"Siz begunoh sehrgarlarni ta'qib qilib, afsun kuchini tugatdingiz. "
                    f"Haqiqiy mahbuslar: {all_f_mentions} tunda guruhni tark etib, butunlay g'oyib bo'lishdi!",
                    parse_mode="HTML"
                )
                AZKABAN_SESSIONS.pop(chat_id, None)
            else:
                bot.reply_to(
                    message,
                    f"❌ {get_mention(target)} shunchaki begunoh talaba! Vazirlik yanglishdi.\n"
                    f"⚠️ Qidiruv guruhida yana <b>{session['attempts']} ta</b> imkoniyat qoldi!",
                    parse_mode="HTML"
                )
        return

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
    
    try:
        sender_member = bot.get_chat_member(message.chat.id, sender.id)
        is_admin = sender_member.status in ['administrator', 'creator']
    except:
        is_admin = False
    
    is_vazir = (sender.id == ADMIN_ID)
    
    if not is_admin and not is_vazir:
        return bot.reply_to(message, f"🧙‍♂️ Kechirasiz {mention_sender}, siz hali oddiy o'quvchisiz! Bunday oliy darajali sehrlarni faqat professorlar ishlata oladi! 🪄")

    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Afsun kuchga kirishi uchun uni biror sehrgarning xabariga (Reply) qaratishingiz kerak!")

    target = message.reply_to_message.from_user
    mention_target = get_mention(target)
    
    if target.id == ADMIN_ID:
        return bot.reply_to(
            message, 
            f"🛡 <b>PROTEGO HORRIBILIS!</b> \n\n{mention_sender}, siz hozirgina <b>Jodu Vazirining</b> shaxsan o'ziga qarshi afsun ishlatishga urindingiz! "
            f"Sizning ojiz afsuningiz vazirlikning qadimiy daxlsiz himoya qalqoniga urilib, dahshatli kuch bilan o'zingizga qaytdi! ⚡️"
        )

    try:
        target_member = bot.get_chat_member(message.chat.id, target.id)
        is_target_admin = target_member.status in ['administrator', 'creator']
    except:
        is_target_admin = False
        
    bot_obj = bot.get_me()

    if (is_target_admin or target.id == bot_obj.id) and not is_vazir:
        return bot.reply_to(message, f"🧙‍♂️ {mention_sender}, boshqa bir professor yoki prefektga qarshi duel e'lon qilish taqiqlangan! Hogwarts nizomiga amal qiling.")

    args = message.text.split()[1:]
    
    try:
        if cmd == "/avadakedavra":
            bot.ban_chat_member(message.chat.id, target.id)
            if is_vazir:
                txt = f"⚖️ <b>SEHRGARLAR VAZIRLIGI OLIY FARMONI!</b>\n\n🦅 Shaxsan <b>Jodu Vazirining</b> muhrlangan buyrug'iga binoan, {mention_target} qora sehrgarlikda va tartibni buzishda ayblanib, daxshatli <b>AVADA KEDAVRA</b> afsuni ostida yashil nur ichida yo'q qilindi va Hogwarts guruhidan abadiy badarg'a etildi! ⛓⚡️"
            else:
                txt = f"⚡️ <b>AVADA KEDAVRA!</b> \n\n{mention_target} yashil nur ichida g'oyib bo'ldi va Hogwarts guruhidan butunlay haydaldi! ⛓"
            bot.send_message(message.chat.id, txt)
        
        elif cmd == "/revive":
            bot.unban_chat_member(message.chat.id, target.id)
            if is_vazir:
                txt = f"📜 <b>SEHRGARLAR VAZIRLIGI AFV ETISH BAYONOTI!</b>\n\n🕊 <b>Jodu Vazirining</b> daxlsiz rahm-shafqati bilan, {mention_target} ustidagi barcha qora sehrlar olib tashlandi! <b>REVIVE</b> afsuni kuchga kirdi va Hogwarts darvozalari u uchun qayta ochildi! ✨"
            else:
                txt = f"🕊 <b>REVIVE!</b> \n\n{mention_target} qayta tiriltirildi va guruh darvozalari unga yana ochildi!"
            bot.send_message(message.chat.id, txt)

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
            
            if is_vazir:
                txt = f"🤫 <b>VAZIRLIKNING MAXFIY SILENCIO BUYRUG'I!</b>\n\n🙊 Jodu Vazirining buyrug'iga asosan {mention_target}ning ovozi mutloq o'chirildi! U <b>{mute_time} daqiqa</b> davomida Sehrgarlar dunyosida og'iz ocha olmaydi!\n📜 <b>Vazir ko'rsatgan sabab:</b> <i>{reason}</i>"
            else:
                txt = f"🙊 <b>SILENCIO!</b> \n\n{mention_target} ovoz o'chirish afsuni ostida qoldi! U {mute_time} daqiqa davomida guruhda gapira olmaydi.\n📜 Sabab: {reason}"
            bot.send_message(message.chat.id, txt)
            
        elif cmd == "/finite":
            bot.restrict_chat_member(message.chat.id, target.id, 
                                     permissions=types.ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
            if is_vazir:
                txt = f"🔊 <b>FINITE INCANTATEM! (VAZIRLIK AFVI)</b>\n\n⚡️ Jodu Vazirining oliy irodasi bilan {mention_target} ustidagi cheklovlar bekor qilindi. Sadoqat bilan so'zlashga ruxsat berildi!"
            else:
                txt = f"🔊 <b>FINITE INCANTATEM!</b> \n\n{mention_target} ustidagi afsun yechildi. Shovqin solmasdan gapirishi mumkin."
            bot.send_message(message.chat.id, txt)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Afsun amalga oshmadi, xatolik: {str(e)}")

# --- START VA TEKSHIRISH ---
@bot.message_handler(commands=["start"])
def start_cmd(message):
    user = message.from_user
    mention_user = get_mention(user)
    text_args = message.text.split()

    if len(text_args) > 1 and text_args[1].startswith("join_"):
        try:
            g_id = int(text_args[1].replace("join_", ""))
        except:
            g_id = None

        if g_id and g_id in AZKABAN_SESSIONS and AZKABAN_SESSIONS[g_id]["status"] == "registration":
            session = AZKABAN_SESSIONS[g_id]
            if user.id in session["players"]:
                return bot.send_message(message.chat.id, f"⚡️ Xavotir olmang, {mention_user}, siz allaqachon qidiruv ro'yxatidasiz!")
            
            session["players"][user.id] = user
            bot.send_message(
                message.chat.id, 
                f"🏰 <b>Muvaffaqiyatli qo'shildingiz!</b>\n\nHurmatli yosh sehrgar {mention_user}, siz Azkaban mahbuslarini qidirish bo'yicha maxsus guruh tarkibiga qo'shildingiz! "
                f"Yaqin soniyalarda sizga maxfiy vazifangiz (rolingiz) yuboriladi. Tayyor turing! 🪄✨"
            )
            bot.send_message(g_id, f"🧙‍♂️ {mention_user} qidiruv guruhiga muvaffaqiyatli safarbar etildi!")
            return
        else:
            return bot.send_message(message.chat.id, "❌ Afsuski, bu o'yinga ro'yxatdan o'tish muddati tugagan yoki o'yin topilmadi.")

    if message.chat.type != 'private':
        bot_info = bot.get_me()
        btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🏰 Shaxsiy chatga o'tish", url=f"https://t.me/{bot_info.username}?start=start")
        )
        txt = f"Hurmatli yosh sehrgar {mention_user}! ⚡\n\nSehrli menyulardan foydalanish uchun men bilan <b>shaxsiy chatda</b> suhbatlashishingizni so'rayman."
        return bot.reply_to(message, txt, reply_markup=btn)

    banned = load_data(BANNED_FILE)
    if str(user.id) in str(banned):
        return bot.send_message(message.chat.id, "Siz Azkabandagi mahbus kabi botdan chetlatilgansiz!")

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
        txt = f"Xush kelibsan, {mention_user}! ⚡\nHogwarts darvozalari ochilishi uchun avval quyidagi guruh va kanalda qayddan o'tishingiz kerak."
        return bot.send_message(message.chat.id, txt, reply_markup=btn)
    
    welcome_txt = f"Salom, {mention_user}! Hogwartsga xush kelibsiz! ✨\nMen sizga eng nodir sehrli kitoblar va kinolarni topishda yordam beraman."
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
        bot.answer_callback_query(callback.id, "Siz hali barcha shartlarni bajarmadinigiz!", show_alert=True)

# --- ADMIN FUNKSIYALARI ---
@bot.message_handler(commands=["getid"])
def get_file_id(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Menga istalgan artefaktni (fayl) yuboring, uning FILE_ID sini o'qib beraman:")
    ADMIN_STATES[message.from_user.id] = "waiting_for_file"

@bot.message_handler(commands=["setwelcome"])
def set_welcome_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Katta Zalda yangi talabalarni kutib olish uchun xabarnoma yuboring ({name} ism o'rniga):")
    ADMIN_STATES[message.from_user.id] = {"state": "waiting_for_welcome_text"}

@bot.message_handler(commands=["admins"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    txt = ("🧙‍♂️ <b>Jodu Vaziri Paneli:</b>\n\n/send - Reklama\n/getid - ID olish\n/setwelcome - Kutib olishni sozlash")
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=["send"])
def ad_start(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "Barcha talabalarga yuboriladigan xabarni kiriting:")
    ADMIN_STATES[message.from_user.id] = "waiting_for_ad"

# --- MATNLAR VA MULTIMEDIA ISHLOVCHI ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_admin_and_text_replies(message):
    uid = message.from_user.id
    text = message.text
    chat_id = message.chat.id

    if message.chat.type != 'private' and chat_id in AZKABAN_SESSIONS:
        session = AZKABAN_SESSIONS[chat_id]
        if session["status"] == "playing" and uid in session["fugitives"]:
            if text and len(text.split()) >= 3:
                session["msg_counts"][uid] += 1
                if session["msg_counts"][uid] >= 7:
                    session["fugitives"].remove(uid)
                    session["escaped_fugitives"].append(uid)
                    bot.send_message(
                        chat_id,
                        f"🏃‍♂️ <b>MAHBUS QOCHIB KETDI!</b>\n\n"
                        f"Ayyor mahbus {get_mention(message.from_user)} suhbat orasida izini butunlay yashirdi va g'oyib bo'ldi! 🌌\n"
                        f"Qolgan yashirin mahbuslar soni: <b>{len(session['fugitives'])}</b>",
                        parse_mode="HTML"
                    )
                    if not session["fugitives"]:
                        bot.send_message(chat_id, "💀 <b>QOCHQINLAR G'ALABASI!</b> Guruhdagi barcha yashirin qochqinlar muvaffaqiyatli qochib qutulishdi!")
                        AZKABAN_SESSIONS.pop(chat_id, None)

    if uid == ADMIN_ID and uid in ADMIN_STATES:
        state_data = ADMIN_STATES[uid]
        
        if state_data == "waiting_for_file":
            f_id = None
            if message.photo: f_id = message.photo[-1].file_id
            elif message.video: f_id = message.video.file_id
            elif message.document: f_id = message.document.file_id
            
            if f_id: bot.send_message(message.chat.id, f"<code>{f_id}</code>")
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
            bot.send_message(message.chat.id, f"✅ Xabar {count} ta sehrgarga yetkazildi.")
            ADMIN_STATES.pop(uid, None)
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_text":
            if message.text:
                ADMIN_STATES[uid] = {"state": "waiting_for_welcome_media", "txt": message.text}
                bot.reply_to(message, "Endi media (rasm yoki video) yuboring:")
            return

        elif isinstance(state_data, dict) and state_data.get("state") == "waiting_for_welcome_media":
            welcome_db = load_data(WELCOME_FILE)
            cid = str(message.chat.id)
            f_id, f_type = None, "text"
            
            if message.photo: f_id, f_type = message.photo[-1].file_id, "photo"
            elif message.video: f_id, f_type = message.video.file_id, "video"

            welcome_db[cid] = {"text": state_data['txt'], "f_id": f_id, "f_type": f_type}
            save_data(WELCOME_FILE, welcome_db)
            bot.send_message(message.chat.id, "✅ Kutib olish tizimi sozlandi!")
            ADMIN_STATES.pop(uid, None)
            return

    if text == "📚 Kitoblar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("📚 Hammasi birda (1-7)", callback_data="get_all_books"),
            types.InlineKeyboardButton("🇺🇿 O'zbekcha tarjima", callback_data="b_uz"),
            types.InlineKeyboardButton("🇬🇧 Original inglizcha", callback_data="b_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Kerakli bo'limni tanlang:", reply_markup=btn)
        
    elif text == "🎬 Kinolar":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="m_uz"),
            types.InlineKeyboardButton("🇷🇺 Ruscha", callback_data="m_ru"),
            types.InlineKeyboardButton("🇬🇧 Inglizcha", callback_data="m_en"),
            types.InlineKeyboardButton("⬅️ Orqaga", callback_data="home")
        )
        bot.send_message(message.chat.id, "Tilni tanlang:", reply_markup=btn)

    elif text == "🎩 Saralovchi shlyapa":
        uid_str = str(message.from_user.id)
        data = load_data(HOUSES_FILE)
        if uid_str not in data:
            data[uid_str] = random.choice(list(HOUSES_DETAILS.keys()))
            save_data(HOUSES_FILE, data)
        
        h = HOUSES_DETAILS[data[uid_str]]
        msg = bot.send_message(message.chat.id, "🧐 <b>Shlyapa ko'zlaringizga tikilib o'ylamoqda... Siz haqingizdagi xotiralarni titkilamoqda...</b>")
        time.sleep(2)
        
        final_text = f"{h['txt']}\n\nSiz munosib bo'lgan fakultet: {h['emoji']} <b>{data[uid_str]}</b>\n🔑 Kirish afsuni: <code>{h['kalit']}</code>"
        shlyapa_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎩 Shlyapaga borish", url=f"https://t.me/{SHLYAPA_USER}"))
        bot.edit_message_text(final_text, message.chat.id, msg.message_id, reply_markup=shlyapa_btn)

    elif text == "🌀 Saralash":
        uid_str = str(message.from_user.id)
        g_data = load_data(GROUPS_FILE)
        if uid_str in g_data:
            current_g = g_data[uid_str]
            return bot.reply_to(message, f"Siz allaqachon sehrli ittifoqqa saralangansiz: <b>{current_g}</b>")
        
        selected_group = random.choice(list(PROJECT_GROUPS.keys()))
        g_data[uid_str] = selected_group
        save_data(GROUPS_FILE, g_data)
        
        g_info = PROJECT_GROUPS[selected_group]
        msg = bot.send_message(message.chat.id, "🔮 <b>Sehrli Ko'zgu porlab, sizning ichki dunyongizni tahlil qilmoqda...</b>")
        time.sleep(2)
        bot.edit_message_text(g_info["txt"], message.chat.id, msg.message_id)

    # --- QO'SHIMCHA 1: PATRONUS TESTI (ANTI-CHEAT BILAN) ---
    elif text == "🦄 Patronus testi":
        uid_str = str(message.from_user.id)
        p_data = load_data(PATRONUS_FILE)
        
        if uid_str in p_data:
            # Aldashga qarshi chora: testni qayta topshira olmaydi, faqat o'zinikini ko'radi
            saved = p_data[uid_str]
            return bot.send_message(
                message.chat.id,
                f"🪄 <b>Siz allaqachon Patronus afsuningizni chaqirgansiz!</b>\n\n"
                f"Sizning xotiralaringiz va qalbingizga bog'langan hayvon: {saved['emoji']} <b>{saved['animal']}</b>\n"
                f"📜 <i>{saved['desc']}</i>\n\n"
                f"⚡️ <i>«Expecto Patronum!» jodusini takrorlaganingizda kumushrang nur aynan shu shaklni oladi.</i>"
            )
            
        msg = bot.send_message(message.chat.id, "🪄 <b>«Expecto Patronum!» afsuni uchun eng baxtli xotirangizni eslang... Qalbingiz siri ochilmoqda...</b>")
        time.sleep(2)
        
        chosen_patronus = random.choice(PATRONUS_SHAPES)
        p_data[uid_str] = chosen_patronus
        save_data(PATRONUS_FILE, p_data)
        
        final_pat_text = (
            f"⚡️ <b>PATRONUS MUVAFFAQIYATLI CHAQIRILDI!</b>\n\n"
            f"Tayoqchangiz uchidan otilib chiqqan yorqin kumushrang nur asta-sekin shakllandi. Sizning Patronusingiz: "
            f"{chosen_patronus['emoji']} <b>{chosen_patronus['animal']}</b>!\n\n"
            f"📜 <b>Ta'rif:</b> {chosen_patronus['desc']}"
        )
        bot.edit_message_text(final_pat_text, message.chat.id, msg.message_id)

    # --- QO'SHIMCHA 2: MA'JUN TAYYORLASH DARSI ---
    elif text == "🧪 Ma'jun tayyorlash":
        msg = bot.send_message(
            message.chat.id, 
            "🧪 <b>Siz Professor Sneypning Ma'junlar darsiga kirdingiz.</b>\n"
            "Qozon ostiga olov yoqildi, ingredientlar tayyorlanmoqda... ⏳"
        )
        time.sleep(2)
        
        # Tasodifiy qoida buzilishi yoki portlash ehtimoli (20%)
        if random.random() < 0.20:
            fail_text = (
                "💥 <b>BOOOOOOOM!!!</b>\n\n"
                "Siz qozon haroratini noto'g'ri sozladingiz yoki ingredientlarni teskari ketma-ketlikda soldingiz! "
                "Qozoningiz qattiq g g'o'ldiradi va dahshatli kuch bilan portlab ketdi! 🪂\n\n"
                "🧹 <i>Tezda buralib turgan quyuq tutunlar tarqalmasidan oldin darsxonani tozalang, Professor Sneyp ko'rib qolsa fakultetingizdan ochkoni ayovsiz chegirib tashlaydi!</i>"
            )
            bot.edit_message_text(fail_text, message.chat.id, msg.message_id)
        else:
            chosen_potion = random.choice(POTIONS_LIST)
            success_text = (
                f"🧪 <b>MA'JUN TAYYOR! (Muvaffaqiyatli dars)</b>\n\n"
                f"Ehtiyotkorlik bilan aralashtirish va qat'iy qoidalarga rioya qilish natijasida siz mukammal "
                f"<b>{chosen_potion['name']}</b> {chosen_potion['emoji']} tayyorlashga muvaffaq bo'ldingiz!\n\n"
                f"📜 <b>Xususiyati:</b> {chosen_potion['desc']}\n\n"
                f"✨ Professor Sneyp sizga norozi qarab qo'ydi, lekin ma'jun sifatiga e'tiroz bildira olmadi. Fakultetingizga +10 ball!"
            )
            bot.edit_message_text(success_text, message.chat.id, msg.message_id)

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
            if conf['f_type'] == "photo": m = bot.send_photo(cid, conf['f_id'], caption=cap, reply_markup=btn)
            elif conf['f_type'] == "video": m = bot.send_video(cid, conf['f_id'], caption=cap, reply_markup=btn)
            else: m = bot.send_message(cid, cap, reply_markup=btn)
            Thread(target=delete_after_delay, args=(message.chat.id, m.message_id, 600)).start()

# --- CALLBACK TUGMALARIGA ISHLOV BERISH ---
@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(callback):
    d = callback.data
    chat_id = callback.message.chat.id
    
    if d == "get_all_books":
        bot.send_document(callback.message.chat.id, ALL_IN_ONE_BOOK["file_id"], caption=ALL_IN_ONE_BOOK["caption"])
        bot.answer_callback_query(callback.id)
        return
        
    if d == "home":
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        bot.send_message(callback.message.chat.id, "Xizmatlar:", reply_markup=main_menu())
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
        bot.edit_message_text("Tomni tanlang:", chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=btn)
        return

    if d.startswith("get_"):
        _, code, idx = d.split("_")
        idx = int(idx)
        if code == "buz": item = BOOKS_UZ[idx]; f = bot.send_document
        elif code == "ben": item = BOOKS_EN[idx]; f = bot.send_document
        elif code == "muz": item = MOVIES_UZ[idx]; f = bot.send_video
        elif code == "mru": item = MOVIES_RU[idx]; f = bot.send_video
        elif code == "men": item = MOVIES_EN[idx]; f = bot.send_video
        
        if not item["file_id"]: bot.send_message(callback.message.chat.id, item["caption"])
        else: f(callback.message.chat.id, item["file_id"], caption=item["caption"])
        bot.answer_callback_query(callback.id)

# --- RENDER PORTINI TINGLOVCHI FLASK SERVER ---
app = Flask('')

@app.route('/')
def home(): return "Hogwarts Bot ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    time.sleep(20)
    while True:
        try: requests.get(RENDER_URL)
        except: pass
        time.sleep(600)

def run_bot():
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except: time.sleep(5)

if __name__ == '__main__':
    Thread(target=run_bot, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()
    run_flask()
