import telebot
import sqlite3
import os
from datetime import datetime, timedelta
from telebot import types

bot = telebot.TeleBot(os.getenv("8712350499:AAGwmKgekyGC6U51pgEhqr8mab2RdCCfjU0"))
conn = sqlite3.connect('tracker.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS shifts 
             (date TEXT PRIMARY KEY, employee TEXT, station TEXT, pieces INTEGER, hours REAL, bonus REAL)''')
conn.commit()

def calc_bonus(pieces, hours):
    if hours <= 0: return 0
    rate = pieces / hours
    norm = 45
    excess = max(0, pieces - norm * hours)
    tiers = [0,7,14,22,29,36,40]
    rates = [0,0.61,0.631,0.651,0.681,0.70,0.72,0.74]
    for i,t in enumerate(tiers):
        if excess <= t: 
            return round(excess * rates[i], 2)
    return round(excess * 0.74, 2)

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, persistent=True)
    markup.row('/send', '/stats')
    markup.row('/month', '/best', '/export')
    bot.send_message(m.chat.id, "AutoDoc OS Tracker", reply_markup=markup)

@bot.message_handler(commands=['send'])
def send(m):
    try:
        _, pieces, hours, station = m.text.split()[:4]
        date = m.text.split()[4] if len(m.text.split())>4 else datetime.now().strftime('%Y-%m-%d')
        emp = m.from_user.first_name
        pieces, hours = int(pieces), float(hours)
        bonus = calc_bonus(pieces, hours)
        c.execute("REPLACE INTO shifts VALUES (?,?,?,?,?,?)", (date, emp, station or "M13", pieces, hours, bonus))
        conn.commit()
        bot.reply_to(m, f"✅ {date} | {station} | {pieces} пик | {hours}ч | +{bonus}zł")
    except:
        bot.reply_to(m, "Формат: /send пики часы [станция] [YYYY-MM-DD]")

@bot.message_handler(commands=['stats'])
def stats(m):
    c.execute("SELECT SUM(pieces), SUM(hours), SUM(bonus) FROM shifts WHERE date >= date('now','-30 day')")
    res = c.fetchone()
    bot.reply_to(m, f"30 дней:\nПики: {res[0]}\nЧасы: {res[1]:.1f}\nПремия: {res[2]:.2f}zł")

# Другие команды (/month, /best, /export) можно добавить позже
bot.infinity_polling()