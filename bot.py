import telebot
import random
import time
import threading
import json
import os
from datetime import datetime
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
        data[uid] = {
            "mode": "good",
            "mood": "calm",
            "invited": [],
            "evil_unlocked": False,
            "history": [],
            "name": "",
            "msg_count": 0
        }
    if "history" not in data[uid]:
        data[uid]["history"] = []
    if "name" not in data[uid]:
        data[uid]["name"] = ""
    if "mood" not in data[uid]:
        data[uid]["mood"] = "calm"
    if "msg_count" not in data[uid]:
        data[uid]["msg_count"] = 0
    return data[uid]


# ==== НАСТРОЕНИЯ ====
MOODS = ["happy", "calm", "sad", "sleepy", "thoughtful"]

MOOD_PREFIX = {
    "happy": ["🙂", "😄", "😊", "", "", "😁"],
    "calm": ["", "", "🙂", ""],
    "sad": ["😔", "эх... ", "", "🙁"],
    "sleepy": ["😴", "эх, спать хочу... ", "", "🥱"],
    "thoughtful": ["🤔", "хм... ", "", "🤨"],
}

MOOD_SUFFIX = {
    "happy": ["!", " 🙂", " 😄", "!", ""],
    "calm": ["", "", ".", "", ""],
    "sad": ["...", " 😔", "", ""],
    "sleepy": ["...", " 😴", "", ""],
    "thoughtful": ["...", " 🤔", "", ""],
}


def get_time_greeting():
    h = datetime.now().hour
    if 5 <= h < 12:
        return "morning"
    elif 12 <= h < 18:
        return "day"
    elif 18 <= h < 23:
        return "evening"
    else:
        return "night"


def mood_from_time():
    """Настроение по времени суток."""
    h = datetime.now().hour
    if 6 <= h < 10:
        return "sleepy"
    elif 10 <= h < 18:
        return "happy"
    elif 18 <= h < 22:
        return "calm"
    else:
        return "thoughtful"


def wrap_with_mood(text, mood):
    """Оборачивает ответ в настроение."""
    prefix = random.choice(MOOD_PREFIX.get(mood, [""]))
    suffix = random.choice(MOOD_SUFFIX.get(mood, [""]))
    return f"{prefix}{text}{suffix}"


BAD_WORDS = [
    "дурак", "идиот", "тупой", "лох ", "дебил", "козёл", "козел",
    "придурок", "чмо", "кретин", "додик", "олух", "болван",
    "тупица", "бестолочь", "недоумок", "баран", "осёл", "осел",
    "хам", "наглец", "нахал", "клоун", "дегенерат", "имбецил",
    "мразь", "тварь", "гнида", "падла", "сволочь", "мерзавец",
    "подлец", "негодяй", "паразит", "отморозок", "лошара",
    "чмошник", "сопляк", "ничтожество", "нищеброд", "гопник",
    "быдло", "быдлан", "нахуй", "нахуя", "похуй", "охуел",
    "заебал", "отъебись", "хуй", "пизд", "блядь", "блят",
    "ебал", "ебан", "сука", "мудак", "гандон", "шлюха",
    "пидор", "долбоёб", "жопа", "говно", "педофил",
]

COUNTER_ATTACKS = [
    "Ой, как грубо 😏", "Сам иди, я тут посижу",
    "Смело. Только неэффективно 🙃", "Так-так, кто-то не в настроении",
    "Ого, аж испугался. Нет, не испугался",
    "Понял, ты у нас главный тут. Корона не жмёт?",
    "Хамство — это, конечно, стиль. Но плохой.",
    "Какой ты дерзкий. В интернете все смелые 😄",
    "Ты в жизни тоже такой или только в чате?",
    "Ух ты, какой герой. Медаль тебе 🏅",
    "Ты хотел меня обидеть? Попробуй ещё раз 🙃",
    "Мне аж приятно стало. Не.", "Ух, какой суровый. Прям страшно. Нет.",
    "Ладно, клоун, цирк уехал. Свободен.",
    "Ты бы делом занялся, чем грубить боту.",
    "Ну-ну, продолжай. Я записываю.",
    "Аж обидно стало. Шутка. Не обидно.",
    "Может, чайку? Успокоишься 😌",
    "Похоже, кто-то не выспался сегодня.",
    "Серьёзно? Это всё, что ты можешь?",
    "Да ладно, ты серьёзно? 😂",
    "Ты чего такой злой? Обними кого-нибудь 🫂",
    "Ну и характер. Тебе бы в цирке работать 🎪",
]


# ==== ТЕМЫ (добрый) ====
TOPICS_GOOD = {
    "привет": ["Привет!", "О, привет 🙂", "Привет-привет!", "Хай ✌️", "Здорово!"],
    "как дела": ["Да норм, а ты?", "Всё хорошо 🙂 ты как?", "Отлично! А у тебя?", "Потихоньку. Ты как?"],
    "что делаешь": ["Да вот, с тобой болтаю 🙂", "Ничего особенного. Ты чем занят?", "Отдыхаю. А ты?"],
    "люблю тебя": ["И я тебя ❤️", "Ты самый лучший 🙂", "Обнимаю 🤗", "Взаимно ❤️"],
    "ты кто": ["Твой друг 🙂", "Просто человек", "Тот, кто всегда рядом", "Lunixz 🙂"],
    "скучно": ["Расскажу анекдот?", "Давай поиграем", "Поговорим о чём-нибудь", "А ты чем обычно развлекаешься?"],
    "мем": ["Кидай мем 🙂", "О, мемы — топ!", "Обожаю мемы 😄"],
    "аниме": ["О, аниме! Что смотришь?", "Какой любимый тайтл?", "Аниме — это жизнь 😎"],
    "игр": ["Во что играешь?", "Какая любимая игра?", "Геймер? 🙂"],
    "музык": ["Что слушаешь?", "Какой жанр любишь?", "Любимый исполнитель?"],
    "фильм": ["Что смотрел последнее?", "Какой любимый фильм?", "Кино — топ 🎬"],
    "спорт": ["Спорт — это хорошо!", "Каким спортом занимаешься?", "Любишь тренировки?"],
    "школа": ["Как в школе дела?", "Учишься или на каникулах?", "Какой класс?"],
    "работа": ["Чем занимаешься?", "Как на работе?", "Интересная работа?"],
    "погода": ["Холодно? или жара?", "У нас серо за окном...", "Люблю такую погоду 🙂"],
    "кофе": ["Кофе бодрит ☕ сколько чашек в день?", "Люблю кофе 🙂"],
    "чай": ["Чай — хорошо ☕ с сахаром?", "Какой чай любишь?"],
    "еда": ["Что любишь поесть?", "Пицца или бургеры?", "Обожаю вкусно поесть 😋"],
    "пицца": ["Пицца — топ 🍕 с чем любишь?", "Обожаю пиццу!"],
    "python": ["О, программист 🐍", "Питон — топ!", "Что пишешь?"],
    "brawl": ["О, Brawl Stars! Кого мейнишь?", "Топ игра 🔥"],
    "бравл": ["Brawl Stars? Кого мейнишь?", "Кубков сколько?"],
    "майн": ["Майнкрафт — классика ⛏️ что строишь?", "Выживание или креатив?"],
    "рэп": ["О, рэп! Кого слушаешь?", "Кто любимый рэпер?"],
    "рок": ["О, рок 🎸 что слушаешь?", "Кто любимая группа?"],
    "футбол": ["За кого болеешь?", "Футбол — топ ⚽"],
}

NEUTRAL_GOOD = [
    "Понял 🙂", "Хм, интересно", "Расскажи ещё", "И что дальше?",
    "Прикольно!", "А что было потом?", "Согласен 🙂", "Действительно",
    "Интересно 🤔", "Понимаю", "Ого!", "Ничего себе!",
]

SHORT_GOOD = ["ага", "ну да", "хм", "ок)", "понял", "ясно", "ага-ага"]

TOPICS_EVIL = {
    "привет": ["О, ты. Чего надо?", "Ну привет. Чё хотел?", "Явился, не запылился."],
    "как дела": ["Лучше всех. А тебе какое дело?", "Норм. Тебе-то что?"],
    "что делаешь": ["Да вот, тебя слушаю. Скукота.", "Ничего. Хоть бы ты отстал."],
    "люблю тебя": ["Ага, конечно.", "Не льсти себе.", "Хм, сомневаюсь."],
    "ты кто": ["Тот, кто умнее тебя.", "Не твоё дело.", "Твоя совесть. Шутка."],
    "скучно": ["Ну так займись чем-нибудь.", "Иди уроки делай.", "Мне тоже скучно с тобой."],
    "мем": ["Свои мемы кидай, тут не цирк.", "Мемы у него."],
    "аниме": ["Аниме? Взрослей уже.", "Очередной анимешник..."],
    "школа": ["Школа? Ну удачи, двоечник.", "Учись, а не в телефоне сиди."],
    "игр": ["Опять игры. Книгу открой."],
    "работа": ["Работа? Ха. Хоть что-то делаешь."],
}
NEUTRAL_EVIL = ["Ну и что?", "И чё?", "Дальше что?", "Ясно.", "Ага, как же."]
SHORT_EVIL = ["ага", "ясно", "ну-ну", "и чё", "ок"]

# ==== РЕАКЦИИ НА ЭМОЦИИ ====
SAD_WORDS = ["плохо", "устал", "грустно", "печально", "тяжело", "депресс", "не могу больше"]
HAPPY_WORDS = ["круто", "ура", "класс", "супер", "отлично", "здорово", "кайф"]


def has_bad_word(text):
    t = text.lower()
    for word in BAD_WORDS:
        if word in t:
            return True
    return False


def has_sad(text):
    t = text.lower()
    return any(w in t for w in SAD_WORDS)


def has_happy(text):
    t = text.lower()
    return any(w in t for w in HAPPY_WORDS)


def build_reply(text, mode, history, name, mood):
    t = text.lower().strip()

    if has_bad_word(text):
        return random.choice(COUNTER_ATTACKS)

    # ==== Поддержка, если грустно ====
    if has_sad(text) and mode == "good":
        return random.choice([
            "Что случилось? Расскажи, если хочешь 🫂",
            "Оу... хочешь поговорить об этом?",
            "Бывает. Может, чайку и отдохнуть? ☕",
            "Печально. Я тут, если что 🙂",
        ])

    # ==== Радость вместе ====
    if has_happy(text) and mode == "good":
        return random.choice([
            "О, круто! 🎉", "Рад за тебя!", "Молодец!", "Супер! 😄",
            "Ух ты! Расскажи подробнее!",
        ])

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

    # Контекст — 3 сообщения
    if history:
        last_user = ""
        for h in reversed(history):
            if h.get("role") == "user":
                last_user = h.get("content", "").lower()
                break

        if last_user:
            for k, v in topics.items():
                if k in last_user:
                    follow_ups = {
                        "привет": ["А ты как?", "Как сам?", "Что нового?"],
                        "как дела": ["А у тебя что нового?", "Расскажи, как сам?"],
                        "работа": ["А давно работаешь?", "Нравится?"],
                        "школа": ["А какие оценки?", "Любимый предмет есть?"],
                        "аниме": ["А какое любимое?", "Советуешь что-нибудь?"],
                        "игр": ["А какая любимая?", "Долго играешь?"],
                    }
                    if k in follow_ups:
                        return random.choice(follow_ups[k])
                    return random.choice(v)

    if name and random.random() < 0.15:
        return random.choice([
            f"{name}, расскажи подробнее",
            f"А что ты думаешь, {name}?",
            f"Интересно, {name} 🙂",
        ])

    # Разная длина ответов
    if random.random() < 0.15:
        return random.choice(short)
    return random.choice(neutral)


@bot.message_handler(commands=["start"])
def cmd_start(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    user["name"] = m.from_user.first_name or ""
    user["mood"] = mood_from_time()
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
                                "🎉 Ты пригласил 3 друзей! Злой режим разблокирован!\nНапиши /evil 😈")
                        except:
                            pass
                    save_data(data)
        except:
            pass

    name = m.from_user.first_name or "друг"
    greeting = get_time_greeting()
    greetings = {
        "morning": f"Доброе утро, {name}! ☀️",
        "day": f"Привет, {name}! 👋",
        "evening": f"Добрый вечер, {name} 🌆",
        "night": f"О, {name}, ты чего не спишь? 🌚",
    }

    bot.send_message(m.chat.id,
        f"{greetings[greeting]}\n\nЯ Lunixz — просто собеседник 🙂\n\n"
        "Команды:\n/mode — режим\n/mood — настроение\n/invite — пригласить\n"
        "/evil — злой (после 3 приглашений)\n/good — добрый\n/reset — сброс")


@bot.message_handler(commands=["mood"])
def cmd_mood(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    mood = user.get("mood", "calm")
    save_data(data)
    moods_ru = {
        "happy": "😊 радостный",
        "calm": "🙂 спокойный",
        "sad": "😔 грустный",
        "sleepy": "😴 сонный",
        "thoughtful": "🤔 задумчивый",
    }
    bot.send_message(m.chat.id, f"Сейчас настроение: {moods_ru.get(mood, '🙂')}")


@bot.message_handler(commands=["mode"])
def cmd_mode(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    save_data(data)
    mode = user.get("mode", "good")
    invited = len(user.get("invited", []))
    unlocked = user.get("evil_unlocked", False)
    text = "Сейчас режим: 😈 злой" if mode == "evil" else "Сейчас режим: 🙂 добрый"
    if not unlocked:
        text += f"\n\nДо злого: пригласи ещё {3 - invited} друга (сейчас {invited}/3)"
    else:
        text += "\n\nЗлой разблокирован ✅ (/evil)"
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
        f"Твоя ссылка:\n{link}\n\nПриглашено: {invited}/3\nОсталось: {need}")


@bot.message_handler(commands=["evil"])
def cmd_evil(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    if not user.get("evil_unlocked", False):
        invited = len(user.get("invited", []))
        save_data(data)
        bot.send_message(m.chat.id,
            f"Злой режим пока закрыт 🔒\n\nПриглашено: {invited}/3\n/invite")
        return
    user["mode"] = "evil"
    user["history"] = []
    save_data(data)
    bot.send_message(m.chat.id, "Ок, теперь я злой 😈")


@bot.message_handler(commands=["good"])
def cmd_good(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    user["mode"] = "good"
    user["history"] = []
    save_data(data)
    bot.send_message(m.chat.id, "Ладно, снова добрый 🙂")


@bot.message_handler(commands=["reset"])
def cmd_reset(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    user["history"] = []
    save_data(data)
    bot.send_message(m.chat.id, "Память очищена 🧹")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(m):
    if m.text.startswith("/"):
        return

    data = load_data()
    user = get_user(data, m.from_user.id)
    mode = user.get("mode", "good")
    name = user.get("name", "") or m.from_user.first_name or "друг"

    # обновляем настроение
    user["msg_count"] = user.get("msg_count", 0) + 1
    if user["msg_count"] % 12 == 0:
        user["mood"] = random.choice(MOODS)
    elif user["mood"] not in MOODS:
        user["mood"] = mood_from_time()

    mood = user["mood"]

    reply = build_reply(m.text, mode, user.get("history", []), name, mood)

    # оборачиваем в настроение (только для не-злого режима)
    if mode != "evil" and len(reply) > 3 and random.random() < 0.6:
        reply = wrap_with_mood(reply, mood)

    user["history"].append({"role": "user", "content": m.text})
    user["history"].append({"role": "assistant", "content": reply})
    user["history"] = user["history"][-6:]
    save_data(data)

    bot.send_chat_action(m.chat.id, "typing")
    time.sleep(random.uniform(1, 2.5))
    bot.send_message(m.chat.id, reply)


@bot.message_handler(content_types=["sticker"])
def on_sticker(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, стикер! 🙂", "Классный 😄", "Хм, интересный", "Прикольно!", "👍", "Ахах 😄"]))


@bot.message_handler(content_types=["photo"])
def on_photo(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, фото! 📸", "Красиво!", "Что это?", "Классный кадр 🙂", "Прикольное фото!", "Ого! 📷"]))


@bot.message_handler(content_types=["video"])
def on_video(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, видео! 🎬", "Что там?", "Интересно 🙂", "Гляну позже 😎"]))


@bot.message_handler(content_types=["voice"])
def on_voice(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, голосовое 🎤", "Что говоришь?", "Слушаю 🙂", "Хм, интересно"]))


@bot.message_handler(content_types=["document"])
def on_document(m):
    bot.send_message(m.chat.id, "О, документ 📄 Спасибо!")


@bot.message_handler(content_types=["audio"])
def on_audio(m):
    bot.send_message(m.chat.id, "О, музыка 🎵 Что слушаешь?")


@bot.message_handler(content_types=["animation"])
def on_gif(m):
    bot.send_message(m.chat.id, "О, гифка! 😄")


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
