import telebot
import sqlite3
import os
from datetime import datetime
from telebot import types

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

conn = sqlite3.connect('tracker.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS shifts 
             (date TEXT PRIMARY KEY, employee TEXT, station TEXT, pieces INTEGER, hours REAL, bonus REAL)''')
conn.commit()

def calc_bonus(pieces, hours):
    if hours <= 0: return 0
    excess = max(0, pieces - 45 * hours)
    tiers = [0,7,14,22,29,36,40]
    rates = [0,0.61,0.631,0.651,0.681,0.70,0.72,0.74]
    for i,t in enumerate(tiers):
        if excess <= t: return round(excess * rates[i], 2)
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
        parts = m.text.split()
        pieces = int(parts[1])
        hours = float(parts[2])
        station = parts[3] if len(parts)>3 else "M13"
        date = parts[4] if len(parts)>4 else datetime.now().strftime('%Y-%m-%d')
        emp = m.from_user.first_name
        bonus = calc_bonus(pieces, hours)
        c.execute("REPLACE INTO shifts VALUES (?,?,?,?,?,?)", (date, emp, station, pieces, hours, bonus))
        conn.commit()
        bot.reply_to(m, f"✅ {date} | {station} | {pieces}п | {hours}ч | +{bonus}zł")
    except:
        bot.reply_to(m, "Формат: /send пики часы [станция] [YYYY-MM-DD]")

@bot.message_handler(commands=['stats'])
def stats(m):
    c.execute("SELECT SUM(pieces), SUM(hours), SUM(bonus) FROM shifts WHERE date >= date('