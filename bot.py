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
    {"name": "🎬 3. Узник Азкабана", "file_id": "BAACAgIAAxkBAAICF2oRVsY83X5ynrcgTqvHXFE83TVwAAInCgACMf9ZS-gYbIiUq-JnOwQ", "caption": "🎬 Название: ГП 3: Уzник Азкабана\n⏱ Время: 2.5 часа\n🌐 Язык: Русский\n🎞 Качество: HD\n📢 Написание: @harry_potter_fans_uz"},
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
        "txt": "🦅 <b>ALBUS DUMBLEDORENING OLIY FARMONI BILAN:</b>\n\nSiz yorug'lik, adolat va qat'iyat timsoli bo'lgan muqaddas <b>Feniks Jamiyati</b> (Order of the Phoenix) safiga loyiq deb topildingiz! ⚡️🕊\n\nYuragingizdagi qat'iy ezgulik va zulmatni parchalovchi yorug'lik kuchi sizni ushbu buyuk ittifoqqa yetakladi. Qiyinchiliklar oldida chekinmang, Albus Dumbledore ishonchini oqlang va loyihalarda haqiqiy yorug'lik sehrini ko'rsating! 🪄✨"
    },
    "Ajal Kasofatlari": {
        "emoji": "💀",
        "txt": "🔥 <b>LORD VOLDEMORTNING DAXSHATLI BUYRUG'I BILAN:</b>\n\nSiz eng qudratli, mag'rur va cheksiz kuch-qudratga intiluvchi daxshatli <b>Ajal Kasofatlari</b> (Death Eaters) ittifoqi safiga kiritildingiz! 💀🐍\n\nSizning o'tkir makringiz, daxshatli mardligingiz va buyuklikka bo'lgan so'nmas chanqog'ingiz Qora Lordning e'tiborini tortdi. Eng murakkab vazifalar, daxshatli sehrlar va haqiqiy quvvat endi siz tomonda! Unutmang, qora muhr sizning bilagingizda mangu porlaydi! 🔥😈"
    }
}

# 🔮 SHLYAPA FRAZALARI (RANG-BARANGLIK UCHUN KENGAYTIRILDI)
SHLYAPA_FRAZALARI = [
    "🧐 <i>Hmm... juda qiziq... Qalbingiz tubida chuqur yashiringan sirlarni ko'rmoqdaman...</i>",
    "🧠 <i>Xotiralaringiz qatlamida ulkan salohiyat yotibdi! Qaysi burilish sizni buyuklikka olib borami?</i>",
    "✨ <i>Ooo! Bu ongda shunchaki jasorat emas, balki g'ayritabiiy intilishlar zanjiri bor... Qayerga joylasam ekan?</i>",
    "🦅 <i>O'tkir zehn va fikrlash doirasi... Yoki do'stlar uchun har narsaga tayyor sodiq yurakmi?</i>",
    "⚡️ <i>Menga tik qarab turgan bu ko'zlarda qat'iyat uchqunlarini ko'ryapman... Shoshilmang, yaxshilab o'ylashim kerak...</i>",
    "🪄 <i>Sehr tayog'ingiz kuchi qayerda eng yuqori cho'qqiga chiqa olishini his qilyapman...</i>",
    "🌌 <i>Ajabo! Bu sehrgarning kelajagi shunchalar yorqin va chalkashki, hatto men ham adashib ketishim munosib!</i>",
    "🐍 <i>Makr va ambitsiyami yoki olijanoblik va mardlik? Qalbingizda ikki buyuk kuch to'qnashmoqda...</i>",
    "📜 <i>Hogwarts tarixida sizdek murakkab xarakterli sehrgarlar juda kam bo'lgan... Keling, taqdiringizni ochamiz!</i>",
    "🔮 <i>Yuragingizning urishi menga aniq yo'lni ko'rsatmoqda, siz munosib bo'lgan maskan...</i>"
]

# 🧪 MA'JUN TAYYORLASH HAQIDA HAQIQIY MA'LUMOTLAR
POTIONS_DATA = [
    {"name": "Felix Felicis (Omad Sharbati)", "emoji": "🧪✨", "ingredients": ["Oltin kukuni", "Zuluk sharbati", "Feniks ko'zyoshi"], "desc": "Sizga 24 soat davomida mutloq omad taqdim etadi!"},
    {"name": "Amortentia (Sevgi ma'juni)", "emoji": "🧪💖", "ingredients": ["Marvarid kukuni", "Yalpiz ekstrakti", "Yal tirgich suv"], "desc": "Dunyodagi eng kuchli va xavfli sevgi ma'juni!"},
    {"name": "Polyjuice Potion (Ko'p qiyofali ma'jun)", "emoji": "🧪🎭", "ingredients": ["Alrauna ildizi", "Ikki shoxli kiyik shoxi", "Suv o'tlari"], "desc": "Istalgan odamning qiyofasiga kirish imkonini beradi!"},
    {"name": "Veritaserum (Haqiqat zardobi)", "emoji": "🧪💧", "ingredients": ["Haqiqat guli", "Tilsimli shabnam", "Ilon tili"], "desc": "Ushbu rangsiz suyuqlikni ichgan odam faqat haqiqatni gapiradi!"},
    {"name": "Draught of Peace (Tinchlik malhami)", "emoji": "🧪🌀", "ingredients": ["Lavanda guli", "Yul g'unajin toshi", "Kumush kukuni"], "desc": "Asabiylik va vahimani zumda yo'qotuvchi sharbat."},
    {"name": "Draught of Living Death (Tirik o'lim damlamasi)", "emoji": "🧪💤", "ingredients": ["Asfodela ildizi", "Shuvoq o'ti EXTRA", "Gallyus sharbati"], "desc": "Odamni hayot belgilari bilinmaydigan chuqur uyquga ketkazadi!"},
    {"name": "Skele-Gro (Suyak o'stiruvchi damlama)", "emoji": "🧪🦴", "ingredients": ["Ajdarho qon kukuni", "Chayon zahri", "Botqoq guli"], "desc": "Yo'qotilgan yoki singan suyaklarni tun bo'yi qayta o'stiradi!"},
    {"name": "Elixir of Life (Hayot eliksiri)", "emoji": "🧪💎", "ingredients": ["Falsafiy tosh bo'lagi", "Sof buloq suvi", "Oltin shabnam"], "desc": "Falsafiy toshdan tayyorlanadigan mangu hayot eliksiri!"},
    {"name": "Pepperup Potion (Isituvchi sharbat)", "emoji": "🧪🔥", "ingredients": ["Qizil garmidori", "Zanjabil ildizi", "Gryffindor olovi"], "desc": "Chunonam isitadiki, odamning quloqlaridan 2 soat davomida tutun chiqadi!"},
    {"name": "Wolfsbane Potion (Bo'ri dori)", "emoji": "🧪🐺", "ingredients": ["Ko'k bo'ri guli", "Kumush eritmasi", "Tun guli ekstrakti"], "desc": "Bo'ri-odamlarga to'lin oyda o'z aqlini saqlab qolishga yordam beradi!"}
]

# ALL INGREDIENTS LIST (9 DISTINCT ITEMS)
ALL_INGREDIENTS = [
    "Oltin kukuni", "Zuluk sharbati", "Feniks ko'zyoshi", 
    "Marvarid kukuni", "Yalpiz ekstrakti", "Alrauna ildizi",
    "Ikki shoxli kiyik shoxi", "Haqiqat guli", "Lavanda guli"
]

# 🦄 TASODIFIY PATRONUSLAR RO'YXATI (YANGI LOGIKA)
RANDOM_PATRONUS_LIST = [
    {"animal": "Baxmal Quyon (Hare) 🐇", "desc": "Bu Patronus juda chaqqon, sezgir va kutilmagan qarorlar qabul qila oladigan sehrgarlarga xosdir. Dushman koʻziga u kichik va zararsiz koʻrinishi mumkin, ammo uning tezligi, manyovrlari va aqlli harakatlari har qanday Dementorni sarosimaga solib qoʻyadi."},
    {"animal": "Aslanzahr Quyosh Sheri (Lion) 🦁", "desc": "Jasorat, sadoqat va bamisoli olovli qalb timsoli. Bu Patronus oʻz egasining ichki kuchidan darak beradi. Sher Patronusi chiqqan sehrgarlar doʻstlarini himoya qilish uchun oxirigacha kurashadi va har qanday zulmatni parchalab tashlaydi."},
    {"animal": "Yashirin Kurashchi — Boʻri (Wolf) 🐺", "desc": "Erkinlikni sevuvchi, yolgʻiz va ayni paytda oʻz toʻdasiga oʻta sadoqatli sehrgarlarning yoʻldoshi. Boʻri nihoyatda kuchli instinktlarga ega boʻlib, xavfni ancha uzoqdan his qiladi va kutilmagan zarba bera oladi."},
    {"animal": "Donishmand Boyqush (Owl) 🦉", "desc": "Kuch faqat mushaklarda emas, aqldadir! Bu Patronus chuqur bilimga intiluvchi, strategik fikrlaydigan va sirli tabiatga ega sehrgarlarni tanlaydi. U Dementorlarning ruhan ezish xususiyatiga qarshi eng mustahkam aqliy qalqondir."},
    {"animal": "Afsonaviy Feniks (Phoenix) 🦅", "desc": "Nihoyatda noyob va sehrli Patronus. Har qanday qiyinchilikdan soʻng qayta tugʻila oladigan, umidini hech qachon uzmaydigan insonlar timsoli. Feniks nuri Dementorlarni shunchaki haydamaydi, balki atrofga qaynoq hayotiy energiya tarqatadi."},
    {"animal": "Chaqqon Tulki (Fox) 🦊", "desc": "Uddabronlik, ayyorlik va oʻtkir zehn belgisi. Tulki Patronusi anʼanaviy usullar ish bermagan joyda har doim noodatiy va aqlli yechim topa oladigan sehrgarlarning eng yaqin yordamchisidir."},
    {"animal": "Ajdaho (Dragon) 🐉", "desc": "Cheksiz qudrat, ehtiros va asov tabiat belgisi. Bu Patronus juda kuchli va mag'rur sehrgarlarda namoyon bo'ladi. Uning kumushrang alandasi Dementorlar guruhini bir lahzada yo'q qilib yuborishga qodir!"},
    {"animal": "Sodiq Olmaxon (Squirrel) 🐿", "desc": "Uddabronlik, harakatchanlik va ajoyib xotira ramzi. Kichkina bo'lishiga qaramay, u o'z tezligi va kutilmagan manyovrlari bilan dushmanning har qanday rejasini chippakka chiqara oladi."}
]

# Guruhdagi majun o'yinlari seanslari bazasi
POTION_GAMES = {}

# --- BAZA FAYLLARI ---
HOUSES_FILE = "user_houses.json"
GROUPS_FILE = "user_project_groups.json"
USERS_FILE = "users_list.json"
WELCOME_FILE = "welcome_settings.json"
BANNED_FILE = "banned_users.json"
PATRONUS_FILE = "user_patronus.json"

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
    markup.add(types.KeyboardButton("📚 Sehrli Kutubxona"), types.KeyboardButton("🎬 Kino Zali"))
    markup.add(types.KeyboardButton("🎩 Saralovchi shlyapa"), types.KeyboardButton("🌀 Ittifoqlar Saralashi"))
    markup.add(types.KeyboardButton("🦄 Patronus testi"))
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
        f"⚠️ Vazirlikda jami <b>{attempts} ta xato quilting</b> imkoniyati bor!\n"
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
                f"Daxshat! {get_mention(target)} haqikatdan ham Azkabandan qochgan mahbus bo'lib chiqdi! "
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
                txt = f"🤫 <b>VAZIRLIKNING MAXFIY SILENCIO BUYRUG'I!</b>\n\n🙊 Jodu Vazirining buyrug'iga asosan {mention_target}ning ovozi mutloq o'chirildi! U <b>{mute_time} daqiqa</b> davomida Sehrgarlar duniaosida og'iz ocha olmaydi!\n📜 <b>Vazir ko'rsatgan sabab:</b> <i>{reason}</i>"
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

# --- MA'JUN O'YINI UCHUN GURUH BUYRUQLARI ---
@bot.message_handler(commands=["potion"])
def start_group_potion(message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        return bot.reply_to(message, "🧪 <b>Ushbu murakkab majun darsi faqat Hogwarts prefektlar guruhida amalga oshiriladi!</b>\nGuruhda /potion buyrug'ini yuboring.", parse_mode="HTML")
    
    user = message.from_user
    potion = random.choice(POTIONS_DATA)
    
    correct_ingredients = potion["ingredients"]
    pool = list(correct_ingredients)
    while len(pool) < 9:
        fake = random.choice(ALL_INGREDIENTS)
        if fake not in pool:
            pool.append(fake)
    random.shuffle(pool)
    
    POTION_GAMES[chat_id] = {
        "user_id": user.id,
        "potion_name": potion["name"],
        "emoji": potion["emoji"],
        "correct": correct_ingredients,
        "selected": [],
        "pool": pool,
        "desc": potion["desc"]
    }
    
    kb = types.InlineKeyboardMarkup(row_width=3)
    for i, ing in enumerate(pool):
        kb.add(types.InlineKeyboardButton(ing, callback_data=f"pot_{chat_id}_{i}"))
        
    txt = (
        f"🧪 {get_mention(user)} <b>Professor Sneypning Ma'junlar darsida yangi vazifa oldi!</b>\n\n"
        f"Tayyorlanishi kerak bo'lgan sehrli dori: <b>{potion['name']}</b> {potion['emoji']}\n"
        f"⚠️ <b>Vazifa:</b> Quyidagi ingredientlar ichidan <b>to'g'ri 3 tasini to'g'ri tartibda</b> ketma-ket tanlang. "
        f"Aks holda qozon portlab ketadi! 🔥"
    )
    bot.send_message(chat_id, txt, reply_markup=kb, parse_mode="HTML")

@bot.message_handler(commands=["potion_rules"])
def show_potion_rules(message):
    txt = (
        "🧪 <b>Hogwarts Ma'junlar Darsi — Qoidalar</b>\n\n"
        "Ushbu sehrli dars faqat guruh interfeysida o'ynaladi! 🪐\n\n"
        "🎯 <b>O'yin tartibi:</b>\n"
        "1️⃣ O'yinchi <code>/potion</code> buyrug'ini berganida unga maxsus kitobiy damlama nomi topshiriladi.\n"
        "2️⃣ Pastda <b>9 ta inline tugma</b> orqali masalliqlar chalkashtirib ko'rsatiladi.\n"
        "3️⃣ O'yinchi damlamaning asliga mos ravishda <b>3 ta to'g'ri masalliqni ketma-ket</b> solishi shart.\n"
        "4️⃣ Agar ketma-ketlik buzilsa yoki xato masalliq qo'shilsa — qozon dahshatli olov bilan portlaydi!\n"
        "5️⃣ To'g'ri tayyorlangan har bir ma'jun uchun fakultetingizga faxriy ballar yoziladi. ✨"
    )
    bot.reply_to(message, txt, parse_mode="HTML")

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
            types.InlineKeyboardButton("🏰 Shaxsiy minoraga kirish", url=f"https://t.me/{bot_info.username}?start=start")
        )
        txt = (
            f"⚡️ <b>Salom, olijanob sehrgar {mention_user}!</b>\n\n"
            f"Hogwartsning oliy sehrli menyulari va interaktiv darslaridan to'liq foydalanish uchun "
            f"quyidagi tugma orqali men bilan <b>shaxsiy chatga (Direct)</b> o'tishingizni so'rayman! 🪄✨"
        )
        return bot.reply_to(message, txt, reply_markup=btn, parse_mode="HTML")

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
            types.InlineKeyboardButton("🦅 Oliy Sehrgarlar Vazirligi", url=f"https://t.me/{CHANNEL[1:]}"),
            types.InlineKeyboardButton("🏰 Hogwarts Elite Ittifoqi", url=f"https://t.me/{GROUP[1:]}"),
            types.InlineKeyboardButton("✅ Shartlarni tekshirish afsuni", callback_data="recheck_sub")
        )
        txt = (
            f"⚡️ <b>Hogwarts darvozalariga xush kelibsiz, {mention_user}!</b>\n\n"
            f"Qadimiy tilsimlar va darvoza himoyachilari sizni ichkariga qo'yishi uchun dastlab quyidagi "
            f"rasmiy guruh va kanallarda qayddan o'tishingiz talab etiladi! Darvozani ochish uchun afsun tugmasini bosing! 🪄🔑"
        )
        return bot.send_message(message.chat.id, txt, reply_markup=btn, parse_mode="HTML")
    
    welcome_txt = (
        f"🔮 <b>Hogwarts Oliy Maktabiga Xush Kelibsiz, {mention_user}!</b> ⚡️\n\n"
        f"Katta zal eshiklari siz uchun ochiq. Men sizga afsonaviy sehrli kitoblar xazinasi, unutilmas kino zallari "
        f"hamda o'z qobiliyatingizni sinash uchun interaktiv darsliklarni taqdim etaman. Tayoqchangizni tayyorlang! ✨🪄"
    )
    bot.send_message(message.chat.id, welcome_txt, reply_markup=main_menu(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "recheck_sub")
def recheck_callback(callback):
    is_subscribed = check_sub(callback.from_user.id)
    if is_subscribed:
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        welcome_txt = f"🔮 <b>Aloqa muvaffaqiyatli! Sehrli olam darvozalari g'ildirab ochildi, marhamat {get_mention(callback.from_user)}!</b> ✨🪄"
        bot.send_message(callback.message.chat.id, welcome_txt, reply_markup=main_menu(), parse_mode="HTML")
    else:
        bot.answer_callback_query(callback.id, "🚫 Tilsim kuchga kirmadi! Guruh va kanalga to'liq a'zo bo'ling!", show_alert=True)

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

    if text == "📚 Sehrli Kutubxona":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("📚 Barcha Qismlar (1-7)", callback_data="get_all_books"),
            types.InlineKeyboardButton("🇺🇿 O'zbekcha Tarjimalar", callback_data="b_uz"),
            types.InlineKeyboardButton("🇬🇧 Original English", callback_data="b_en"),
            types.InlineKeyboardButton("⬅️ Bosh Menyu", callback_data="home")
        )
        bot.send_message(message.chat.id, "📖 <b>Hogwarts qadimiy qo'lyozmalar bo'limi. Kerakli jildni tanlang:</b>", reply_markup=btn, parse_mode="HTML")
        
    elif text == "🎬 Kino Zali":
        btn = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton("🇺🇿 O'zbekcha Dublyaj", callback_data="m_uz"),
            types.InlineKeyboardButton("🇷🇺 Ruscha Tarjima", callback_data="m_ru"),
            types.InlineKeyboardButton("🇬🇧 Original English", callback_data="m_en"),
            types.InlineKeyboardButton("⬅️ Bosh Menyu", callback_data="home")
        )
        bot.send_message(message.chat.id, "🎬 <b>Ommaviy ko'rish zali. Tasvirlar tilini muhrlang:</b>", reply_markup=btn, parse_mode="HTML")

    elif text == "🎩 Saralovchi shlyapa":
        uid_str = str(message.from_user.id)
        data = load_data(HOUSES_FILE)
        if uid_str not in data:
            data[uid_str] = random.choice(list(HOUSES_DETAILS.keys()))
            save_data(HOUSES_FILE, data)
        
        h = HOUSES_DETAILS[data[uid_str]]
        rand_phrase = random.choice(SHLYAPA_FRAZALARI)
        
        msg = bot.send_message(message.chat.id, f"🎩 <b>{rand_phrase}</b>")
        time.sleep(2.5)
        
        final_text = f"{h['txt']}\n\nSiz munosib bo'lgan fakultet: {h['emoji']} <b>{data[uid_str]}</b>\n🔑 Kirish afsuni: <code>{h['kalit']}</code>"
        shlyapa_btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎩 Shlyapa Minorasiga o'tish", url=f"https://t.me/{SHLYAPA_USER}"))
        bot.edit_message_text(final_text, message.chat.id, msg.message_id, reply_markup=shlyapa_btn, parse_mode="HTML")

    elif text == "🌀 Ittifoqlar Saralashi":
        uid_str = str(message.from_user.id)
        g_data = load_data(GROUPS_FILE)
        if uid_str in g_data:
            current_g = g_data[uid_str]
            return bot.reply_to(message, f"🔮 <b>Sehrli ko'zgu rad etdi!</b> Siz allaqachon oliy ittifoq safiga biriktirilgansiz: <b>{current_g}</b>", parse_mode="HTML")
        
        selected_group = random.choice(list(PROJECT_GROUPS.keys()))
        g_data[uid_str] = selected_group
        save_data(GROUPS_FILE, g_data)
        
        g_info = PROJECT_GROUPS[selected_group]
        msg = bot.send_message(message.chat.id, "🔮 <b>Sehrli Ko'zgu porlab, sizning ichki qon hislatlaringizni tahlil qilmoqda...</b>")
        time.sleep(2.5)
        bot.edit_message_text(g_info["txt"], message.chat.id, msg.message_id, parse_mode="HTML")

    # --- TASODIFIY PATRONUS CHIQARISH LOGIKASI (YANGILANDI) ---
    elif text == "🦄 Patronus testi":
        uid_str = str(message.from_user.id)
        p_data = load_data(PATRONUS_FILE)
        
        # Agar foydalanuvchi oldin aniqlagan bo'lsa, o'sha patronusini qaytaramiz
        if uid_str in p_data:
            saved = p_data[uid_str]
            return bot.send_message(
                message.chat.id,
                f"🪄 <b>Qadimiy taqiq afsuni!</b>\n\nSiz allaqachon o'z qalbingiz tubidagi Patronus jonzotini chaqirib bo'lgansiz! "
                f"Sehrgarning tabiati va uning eng baxtli xotiralari o'zgarmasdir. Sizning Patronusingiz:\n\n"
                f"✨ <b>{saved['animal']}</b>\n\n"
                f"<blockquote><b>Xarakteristikasi:</b> {saved['desc']}</blockquote>\n\n"
                f"⚡️ <i>«Expecto Patronum!» deganingizda, tayog'ingizdan faqat shu nur chiqadi!</i>",
                parse_mode="HTML"
            )
            
        # Agar yangi bo'lsa, tayoqchani silkitish effekti bilan tasodifiy bittasini tanlaymiz
        chosen = random.choice(RANDOM_PATRONUS_LIST)
        p_data[uid_str] = chosen
        save_data(PATRONUS_FILE, p_data)
        
        msg = bot.send_message(message.chat.id, "✨ <b>Sehrli tayoqchani silkitamiz...</b> ✨\n<i>Qani, diqqat qiling, kumushrang nur ichidan qanday jonivor chiqarkon...</i>")
        time.sleep(2.5)
        
        txt = (
            f"⚡️ <b>EXPECTO PATRONUM!!!</b> ⚡️\n\n"
            f"🪄 <b>Sizning Patronusingiz: {chosen['animal']}</b>\n\n"
            f"<blockquote><b>Xarakteristikasi:</b> {chosen['desc']}</blockquote>\n\n"
            f"✨ <i>Ushbu jonivor endi sizni har qanday zulmat va Dementorlardan himoya qiladi!</i>"
        )
        bot.edit_message_text(txt, message.chat.id, msg.message_id, parse_mode="HTML")

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
    
    # --- MA'JUN TAYYORLASH GURUH LOGIKASI ---
    if d.startswith("pot_"):
        _, g_id_str, idx_str = d.split("_")
        g_id = int(g_id_str)
        idx = int(idx_str)
        
        if g_id not in POTION_GAMES:
            return bot.answer_callback_query(callback.id, "❌ Bu ma'jun darsi muddati o'tgan yoki yakunlangan!", show_alert=True)
            
        game = POTION_GAMES[g_id]
        if callback.from_user.id != game["user_id"]:
            return bot.answer_callback_query(callback.id, "🧙‍♂️ Bu darslik faqat /potion buyrug'ini bergan sehrgarga tegishli!", show_alert=True)
            
        chosen_item = game["pool"][idx]
        if chosen_item in game["selected"]:
            return bot.answer_callback_query(callback.id, "⚠️ Bu ingredient qozonga solingan!", show_alert=True)
            
        game["selected"].append(chosen_item)
        current_step = len(game["selected"])
        
        correct_needed = game["correct"][current_step - 1]
        
        if chosen_item != correct_needed:
            bot.answer_callback_query(callback.id, "💥 XATO INGREDIENT!", show_alert=False)
            fail_text = (
                f"💥 <b>BOOOOOOOOM!!!</b>\n\n"
                f"{get_mention(callback.from_user)} qozonga noto'g'ri masalliq yoki ketma-ketlikni aralashtirib yubordi! "
                f"Qozon dahshatli yashil nur bilan portlab ketdi! 🪂\n\n"
                f"🧪 <b>Aslida nima solish kerak edi:</b> {', '.join(game['correct'])}\n"
                f"🧹 <i>Professor Sneyp sizga g'azab bilan qaramoqda. Fakultetingizdan 15 ball chegirildi!</i>"
            )
            bot.edit_message_text(fail_text, g_id, callback.message.message_id, parse_mode="HTML")
            POTION_GAMES.pop(g_id, None)
            return
            
        if current_step == 3:
            bot.answer_callback_query(callback.id, "✅ Muvaffaqiyatli bosqich!", show_alert=False)
            success_text = (
                f"🧪 <b>MUVAFFAQIYATLI MA'JUN! DARS TUGADI!</b>\n\n"
                f"{get_mention(callback.from_user)} qat'iy qoidalarga rioya qilib, eng yuqori aniqlikda "
                f"<b>{game['potion_name']}</b> {game['emoji']} tayyorlashga erishdi!\n\n"
                f"📜 <b>Xususiyati:</b> {game['desc']}\n"
                f"✨ <i>Professor Sneyp daftarga yozib qo'ydi: Fakultetingizga mukammal tayyorlov uchun +20 ball!</i>"
            )
            bot.edit_message_text(success_text, g_id, callback.message.message_id, parse_mode="HTML")
            POTION_GAMES.pop(g_id, None)
        else:
            bot.answer_callback_query(callback.id, f"ingredient {current_step}/3 solindi", show_alert=False)
            txt = (
                f"🧪 {get_mention(callback.from_user)} <b>dorini tayyorlashda davom etmoqda...</b>\n"
                f"Hozirgi holat: Jami 3 tadan {current_step} ta masalliq to'g'ri solindi.\n"
                f"Ketma-ketlikni buzmang, keyingi to'g'ri masalliqni tanlang!"
            )
            kb = types.InlineKeyboardMarkup(row_width=3)
            for i, ing in enumerate(game["pool"]):
                if ing in game["selected"]:
                    kb.add(types.InlineKeyboardButton(f"📥 {ing}", callback_data="dummy"))
                else:
                    kb.add(types.InlineKeyboardButton(ing, callback_data=f"pot_{g_id}_{i}"))
            bot.edit_message_text(txt, g_id, callback.message.message_id, reply_markup=kb, parse_mode="HTML")
        return

    if d == "get_all_books":
        bot.send_document(callback.message.chat.id, ALL_IN_ONE_BOOK["file_id"], caption=ALL_IN_ONE_BOOK["caption"])
        bot.answer_callback_query(callback.id)
        return
        
    if d == "home":
        try: bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except: pass
        bot.send_message(callback.message.chat.id, "📜 <b>Hogwarts minorasi xizmatlari qayta tiklandi:</b>", reply_markup=main_menu(), parse_mode="HTML")
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
        btn.add(types.InlineKeyboardButton("⬅️ Bosh Menyu", callback_data="home"))
        bot.edit_message_text("📖 <b>Kerakli tomni tanlang:</b>", chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=btn, parse_mode="HTML")
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
