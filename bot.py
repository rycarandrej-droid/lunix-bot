import telebot
import random
import time
import threading
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "users.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"mode": "good", "invited": [], "evil_unlocked": False}
    return data[uid]


TOPICS_GOOD = {
    "привет": ["Привет!", "О, привет 🙂", "Привет-привет!", "Хай ✌️"],
    "как дела": ["Да норм, а ты?", "Всё хорошо 🙂 ты как?", "Отлично! А у тебя?"],
    "люблю тебя": ["И я тебя ❤️", "Ты самый лучший 🙂", "Обнимаю 🤗"],
    "ты кто": ["Твой друг 🙂", "Просто человек", "Тот, кто всегда рядом"],
    "скучно": ["Расскажу анекдот?", "Давай поиграем", "Поговорим о чём-нибудь"],
    "мама": ["Мама — это святое ❤️", "Передай ей привет!"],
    "папа": ["Уважение отцу 🙌", "Как он там?"],
    "спасибо": ["Всегда пожалуйста 🙂", "Обращайся!"],
    "пока": ["Пока! 👋", "До связи", "Ещё увидимся 🙂"],
    "ты бот": ["Нет, я человек 🙂"],
    "brawl stars": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥 сколько кубков?"],
    "бравл": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥"],
    "майн": ["Майнкрафт — классика ⛏️ что строишь?"],
    "мем": ["Кидай мем 🙂", "О, мемы — топ!"],
    "аниме": ["О, аниме! Что смотришь?"],
    "кофе": ["Кофе бодрит ☕ сколько чашек в день?"],
    "школа": ["Как в школе дела?"],
    "игр": ["Во что играешь?"],
    "музык": ["Что слушаешь?"],
    "фильм": ["Что смотрел последнее?"],
    "python": ["О, программист 🐍"],
}

NEUTRAL_GOOD = ["Понял 🙂", "Хм, интересно", "Расскажи ещё", "И что дальше?"]
SHORT_GOOD = ["ага", "ну да", "хм", "ок)", "понял"]

TOPICS_EVIL = {
    "привет": ["О, ты. Чего надо?", "Ну привет. Чё хотел?", "Явился, не запылился."],
    "как дела": ["Лучше всех. А тебе какое дело?", "Норм. Тебе-то что?", "Отлично, в отличие от некоторых."],
    "люблю тебя": ["Ага, конечно. Все так говорят.", "Не льсти себе.", "Хм, сомневаюсь."],
    "ты кто": ["Тот, кто умнее тебя. Очевидно.", "Твоя совесть. Шучу, её у тебя нет.", "Не твоё дело."],
    "скучно": ["Ну так займись чем-нибудь. Я тебе не клоун.", "Скучно ему. Мне тоже с тобой не весело.", "Иди уроки делай."],
    "мама": ["Мама — святое. В отличие от тебя.", "Передай ей, что ей не повезло с ребёнком."],
    "папа": ["Уважение отцу. Тебе бы поучиться.", "Папа бы тобой не гордился."],
    "спасибо": ["Не за что. Серьёзно, вообще не за что.", "Ага, не за что."],
    "пока": ["Наконец-то.", "Скатертью дорога.", "Давай, не скучай."],
    "ты бот": ["Сам ты бот. Я умнее тебя.", "Ну и что? Тебе-то что?"],
    "brawl stars": ["Опять в эти игры играешь. Делом займись.", "Ну и качайся дальше, бездарь."],
    "бравл": ["Опять в Brawl? Делом бы занялся."],
    "майн": ["Майнкрафт. Классика для скучных людей."],
    "мем": ["Свои мемы кидай, тут не цирк.", "Мемы у него. Иди работай."],
    "аниме": ["Аниме? Серьёзно? Взрослей уже.", "Очередной анимешник..."],
    "кофе": ["Кофе? Зубы пожалей.", "Пей, только потом не жалуйся на сердце."],
    "школа": ["Школа? Ну удачи, двоечник.", "Учись, а не в телефоне сиди."],
    "игр": ["Опять игры. Хоть раз книгу открой."],
    "музык": ["Музыка у него. Наверное, шлак какой-то слушаешь."],
    "фильм": ["Фильмы он смотрит. Лучше бы делом занялся."],
    "python": ["Программист, значит. Покажи что написал? А, ничего."],
}

NEUTRAL_EVIL = ["Ну и что?", "И чё?", "Дальше что?", "Ясно.", "Ага, как же."]
SHORT_EVIL = ["ага", "ясно", "ну-ну", "и чё", "ок"]


def get_reply(text, mode):
    t = text.lower().strip()
    if mode == "evil":
        topics = TOPICS_EVIL
        neutral = NEUTRAL_EVIL
        short = SHORT_EVIL
    else:
        topics = TOPICS_GOOD
        neutral = NEUTRAL_GOOD
        short = SHORT_GOOD
    for k, v in topics.items():
        if k in t:
            return random.choice(v)
    if len(t) <= 4:
        return random.choice(short)
    return random.choice(neutral)


@bot.message_handler(commands=["start"])
def cmd_start(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    save_data(data)
    args = m.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            inviter_id = args[1].replace("ref_", "")
            if inviter_id != str(m.from_user.id):
                inviter = get_user(data, inviter_id)
                if str(m.from_user.id) not in inviter["invited"]:
                    inviter["invited"].append(str(m.from_user.id))
                    if len(inviter["invited"]) >= 3 and not inviter["evil_unlocked"]:
                        inviter["evil_unlocked"] = True
                        try:
                            bot.send_message(int(inviter_id),
                                "🎉 Ты пригласил 3 друзей! Злой режим разблокирован!\nНапиши /evil, чтобы переключиться 😈")
                        except:
                            pass
                    save_data(data)
        except:
            pass
    name = m.from_user.first_name or "друг"
    bot.send_message(m.chat.id,
        f"Привет, {name}! 👋\n\nЯ просто собеседник 🙂\n\n"
        "Команды:\n/mode — какой режим\n/invite — пригласить друзей\n/evil — стать злым (после 3 приглашений)\n/good — добрый режим")


@bot.message_handler(commands=["mode"])
def cmd_mode(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    save_data(data)
    mode = user.get("mode", "good")
    invited = len(user.get("invited", []))
    unlocked = user.get("evil_unlocked", False)
    if mode == "evil":
        text = "Сейчас режим: 😈 злой"
    else:
        text = "Сейчас режим: 🙂 добрый"
    if not unlocked:
        text += f"\n\nДо злого: пригласи ещё {3 - invited} друга (сейчас {invited}/3)"
    else:
        text += "\n\nЗлой режим разблокирован ✅ (команда /evil)"
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=["invite"])
def cmd_invite(m):
    uid = m.from_user.id
    link = f"https://t.me/lunixz7_bot?start=ref_{uid}"
    data = load_data()
    user = get_user(data, uid)
    save_data(data)
    invited = len(user.get("invited", []))
    need = max(0, 3 - invited)
    bot.send_message(m.chat.id,
        f"Твоя ссылка:\n{link}\n\nПриглашено: {invited}/3\nОсталось: {need}\n\nЗа каждого друга — плюс 😈")


@bot.message_handler(commands=["evil"])
def cmd_evil(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    if not user.get("evil_unlocked", False):
        invited = len(user.get("invited", []))
        save_data(data)
        bot.send_message(m.chat.id,
            f"Злой режим пока закрыт 🔒\n\nПриглашено: {invited}/3\nНапиши /invite для ссылки.")
        return
    user["mode"] = "evil"
    save_data(data)
    bot.send_message(m.chat.id, "Ок, теперь я злой 😈 Не жалуйся.")


@bot.message_handler(commands=["good"])
def cmd_good(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    user["mode"] = "good"
    save_data(data)
    bot.send_message(m.chat.id, "Ладно, снова добрый 🙂")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(m):
    if m.text.startswith("/"):
        return
    data = load_data()
    user = get_user(data, m.from_user.id)
    mode = user.get("mode", "good")
    save_data(data)
    time.sleep(1)
    bot.send_message(m.chat.id, get_reply(m.text, mode))


@bot.message_handler(func=lambda m: True)
def other(m):
    bot.send_message(m.chat.id, "Не вижу текста 🤔")


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
