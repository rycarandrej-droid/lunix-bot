import telebot
import random
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

BOT_TOKEN = "8243071438:AAG_X8EAh2ytlrdt-pjAi6Mmrb2RmLfSoY4"

bot = telebot.TeleBot(BOT_TOKEN)

TOPICS = {
    "привет": ["Привет", "О, привет!"],
    "как дела": ["Да норм, а ты?", "Всё хорошо, ты как?"],
    "работа": ["Чем занимаешься?", "О, интересно"],
    "погода": ["Холодно? или жара?"],
    "музык": ["Что слушаешь?"],
    "фильм": ["Что смотрел последнее?"],
    "python": ["О, программист"],
    "люблю тебя": ["И я тебя ❤️", "Ты самый лучший 🙂", "Обнимаю 🤗"],
    "ты кто": ["Твой друг 🙂", "Просто человек", "Тот, кто всегда рядом"],
    "скучно": ["Расскажу анекдот?", "Давай поиграем", "Поговорим о чём-нибудь"],
    "мама": ["Мама — это святое ❤️", "Передай ей привет!"],
    "папа": ["Уважение отцу 🙌", "Как он там?"],
    "спасибо": ["Всегда пожалуйста", "Обращайся!"],
    "пока": ["Пока!", "До связи"],
    "ты бот": ["Нет, я человек 🙂"],
    "brawl stars": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥 сколько кубков?"],
    "brawl": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥 сколько кубков?"],
    "бравл": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥 сколько кубков?"],
    "майн": ["Майнкрафт — классика ⛏️ что строишь?", "Выживание или креатив?"],
    "мем": ["Кидай мем 🙂", "О, мемы — топ!"],
    "рэп": ["О, рэп! Кого слушаешь?"],
    "кофе": ["Кофе бодрит ☕ сколько чашек в день?"],
    "школа": ["Как в школе дела?"],
}

NEUTRAL = ["Понял", "Хм, интересно", "Расскажи ещё", "И что дальше?"]
SHORT = ["ага", "ну да", "хм", "ок)", "понял"]


def get_reply(text):
    t = text.lower().strip()
    for k, v in TOPICS.items():
        if k in t:
            return random.choice(v)
    if len(t) <= 4:
        return random.choice(SHORT)
    return random.choice(NEUTRAL)


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "Привет!")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(m):
    time.sleep(1)
    bot.send_message(m.chat.id, get_reply(m.text))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


print("Запущено...")
threading.Thread(target=run_web_server, daemon=True).start()
bot.infinity_polling()
