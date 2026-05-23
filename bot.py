import telebot
from telebot import types
import requests

BOT_TOKEN = "8892367862:AAHvyIJCAqVYImehToiKNEVdbo3fOB4seW8"
CHANNEL_ID = "@qamashiakm"
GROQ_KEY = "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"

bot = telebot.TeleBot(BOT_TOKEN)

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def ask_ai(text):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "Foydalanuvchi " + text + " janridagi kitob sorayapti. 3 ta kitob tavsiya qil. Har biri uchun nomi, muallifi, qisqacha mazmuni. Uzbek tilida yoz."}]},
            timeout=30)
        j = r.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        return "Hozir javob bera olmadim."
    except:
        return "Xatolik yuz berdi."

@bot.message_handler(commands=["start"])
def start(message):
    if check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, "Kitob janrini yozing:\nMasalan: psixologiya, roman, tarix, biznes")
    else:
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("Kanalga obuna", url="https://t.me/qamashiakm"))
        m.add(types.InlineKeyboardButton("Tekshirish", callback_data="check"))
        bot.send_message(message.chat.id, "Botdan foydalanish uchun kanalga obuna boing!", reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data=="check")
def check(call):
    if check_subscription(call.from_user.id):
        bot.send_message(call.message.chat.id, "Kitob janrini yozing:")
    else:
        bot.answer_callback_query(call.id, "Obuna bolmagansiz!")

@bot.message_handler(func=lambda m: True)
def recommend(message):
    if not check_subscription(message.from_user.id):
        start(message)
        return
    bot.send_message(message.chat.id, "Qidiryapman...")
    bot.send_message(message.chat.id, ask_ai(message.text))

bot.polling()
