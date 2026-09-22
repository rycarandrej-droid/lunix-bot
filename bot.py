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
            "msg_count": 0,
            "last_action": ""
        }
    for k, v in [("history", []), ("name", ""), ("mood", "calm"),
                  ("msg_count", 0), ("last_action", "")]:
        if k not in data[uid]:
            data[uid][k] = v
    return data[uid]


JOKES = [
    "— Доктор, я думаю, у меня провалы в памяти.\n— И давно это у вас?\n— Что именно?",
    "Программист ставит на ночь два стакана: один с водой — если захочет пить, второй пустой — если не захочет.",
    "Штирлиц открыл дверь. Дверь была закрыта. Штирлиц закрыл дверь. Дверь была открыта. Штирлиц понял: он открывает и закрывает дверь.",
    "— Как дела?\n— Как в сказке.\n— А что в сказке?\n— Чем дальше, тем страшнее.",
    "Оптимист верит, что мы живём в лучшем из миров. Пессимист боится, что это так и есть.",
    "Учёные выяснили: если человек смеётся, значит, ему хорошо. Если человек не смеётся, значит, он программист.",
    "— Что сказал один кекс другому?\n— Я от тебя балдею!",
    "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что OCT 31 == DEC 25.",
    "Сын спрашивает у отца-программиста:\n— Пап, а почему солнце встаёт на востоке?\n— Работает? Не трогай!",
    "— Как поймать программиста?\n— Насыпать на дорожку 1 и 0.",
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
    "Мне аж приятно стало. Не.",
    "Ух, какой суровый. Прям страшно. Нет.",
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
    "Слушай, а ты в жизни такой же смелый? 😏",
    "Такие слова, а сам небось в тапках сидишь.",
    "Как мило. Мне очень важно твоё мнение. Нет, не важно.",
]

BAD_WORDS = [
    "дурак", "дурень", "дуреха", "идиот", "туп", "лох", "дебил",
    "козёл", "козел", "козлин", "придурок", "чмо", "кретин", "додик",
    "олух", "болван", "бестолоч", "недоумок", "баран", "осёл", "осел",
    "хам", "хамло", "наглец", "нахал", "клоун", "дегенерат", "имбецил",
    "мраз", "твар", "гнид", "падл", "сволоч", "мерзав", "подлец",
    "негодя", "паразит", "отмороз", "лошар", "чмошник", "сопляк",
    "ничтожеств", "нищеброд", "гопник", "быдл", "шваль", "шантрап",
    "псих", "шизик", "ненормальн", "придурошн", "придурк",
    "хуй", "хуя", "хую", "хуё", "хуи", "хуйн", "хуйня",
    "пизд", "пиздец", "пизда", "пизди", "пизду", "пизды",
    "бляд", "блят", "блядь", "бляди", "блятск",
    "ебал", "ебан", "ебат", "ебуч", "ебля", "ебну", "ебёт",
    "ёбал", "ёбан", "ёбат", "ёбуч", "ёбля", "ёбну", "ёбёт",
    "заеба", "заёба", "заебис", "заёбис", "заебал", "заёбал",
    "отъеб", "отъёб", "отъебис", "отъёбис",
    "выеб", "выёб", "въеб", "въёб", "наеб", "наёб",
    "долбоёб", "долбоеб", "долбоящер", "долбо",
    "сук", "сука", "суки", "суч", "сучк", "сучон", "сучён",
    "мудак", "мудил", "мудень", "мудозвон", "муд",
    "гандон", "гондон", "гандо", "гондо",
    "шлюх", "шалав", "шалавы", "шлюш",
    "дроч", "дрочи", "дрочун", "дрочк",
    "залуп", "залупой", "залупи",
    "мандав", "мандавошк", "манда",
    "пидор", "пидар", "пидр", "пидормот",
    "педик", "гомик", "гомосек",
    "жоп", "жопа", "жопу", "жопой", "жопная",
    "говн", "говно", "говнюк", "говнищ", "говнюш",
    "срак", "срака", "срать", "срал", "срёт",
    "сса", "ссать", "ссы", "ссыкло", "ссыкун",
    "похуй", "похую", "похуис", "похуист",
    "нахуй", "нахуя", "нахуярь",
    "охуе", "охуел", "охуенно", "охуительн", "охуеть",
    "ахуе", "ахуел", "ахуенно", "ахуительн", "ахуеть",
    "хуесос", "хуеплёт", "хуеплет",
    "педофил", "педофилк",
    "скотин", "скотоеб", "скотобаз",
    "ублюд", "ублюдок", "выродок", "выродк",
    "подонок", "подонк", "урод", "уродк", "уродина",
    "помой", "помойк", "шавк", "шавка",
    "псин", "псина", "свинь", "свинья",
    "крыс", "крыса", "зме", "змея", "гиен", "гиена",
    "дебилоид", "кретиноид", "тупоголов", "твердолоб",
    "пустоголов", "чугунк",
]

FEAR_WORDS = [
    "страшно", "боюсь", "тревога", "тревожно", "не могу уснуть",
    "бессонниц", "одиноко", "паника", "кошмар", "жутко", "бабайка",
    "страх", "ужас", "паническ", "трясёт", "трясет", "не по себе",
    "плохо", "тяжело", "депресс", "грустно", "печально", "тоскливо",
    "плачу", "слёзы", "слезы", "больно", "обидно", "устал",
  ]
MOODS = ["happy", "calm", "sad", "sleepy", "thoughtful"]

MOOD_PREFIX = {
    "happy": ["🙂", "😄", "😊", "", ""],
    "calm": ["", "", "🙂", ""],
    "sad": ["😔", "эх... ", "", ""],
    "sleepy": ["😴", "эх, спать хочу... ", "", ""],
    "thoughtful": ["🤔", "хм... ", "", ""],
}

MOOD_SUFFIX = {
    "happy": ["!", " 🙂", " 😄", "", ""],
    "calm": ["", "", ".", ""],
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
    prefix = random.choice(MOOD_PREFIX.get(mood, [""]))
    suffix = random.choice(MOOD_SUFFIX.get(mood, [""]))
    return f"{prefix}{text}{suffix}"


TOPICS_GOOD = {
    "привет": ["Привет!", "О, привет 🙂", "Привет-привет!", "Хай ✌️"],
    "как дела": ["Да норм, а ты?", "Всё хорошо 🙂 ты как?", "Отлично! А у тебя?"],
    "что делаешь": ["Да вот, с тобой болтаю 🙂", "Ничего особенного. Ты чем занят?"],
    "люблю тебя": ["И я тебя ❤️", "Ты самый лучший 🙂", "Обнимаю 🤗"],
    "ты кто": ["Твой друг 🙂", "Просто человек", "Тот, кто всегда рядом"],
    "скучно": ["Расскажу анекдот?", "Давай поиграем", "Поговорим о чём-нибудь"],
    "мем": ["Кидай мем 🙂", "О, мемы — топ!"],
    "аниме": ["О, аниме! Что смотришь?", "Какой любимый тайтл?"],
    "игр": ["Во что играешь?", "Какая любимая игра?"],
    "музык": ["Что слушаешь?", "Какой жанр любишь?"],
    "фильм": ["Что смотрел последнее?", "Какой любимый фильм?"],
    "спорт": ["Спорт — это хорошо!", "Каким спортом занимаешься?"],
    "школа": ["Как в школе дела?", "Какой класс?"],
    "работа": ["Чем занимаешься?", "Интересная работа?"],
    "погода": ["Холодно? или жара?", "Люблю такую погоду 🙂"],
    "кофе": ["Кофе бодрит ☕"],
    "чай": ["Чай — хорошо ☕"],
    "еда": ["Что любишь поесть?", "Пицца или бургеры?"],
    "пицца": ["Пицца — топ 🍕 с чем любишь?"],
    "python": ["О, программист 🐍", "Питон — топ!"],
    "brawl": ["О, Brawl Stars! Кого мейнишь?"],
    "бравл": ["Brawl Stars? Кого мейнишь?"],
    "майн": ["Майнкрафт — классика ⛏️"],
    "рэп": ["О, рэп! Кого слушаешь?"],
    "рок": ["О, рок 🎸 что слушаешь?"],
    "футбол": ["За кого болеешь?"],
    "умеешь": [
        "Могу болтать 🙂 Анекдот рассказать, в кубик сыграть, монетку бросить 🎲",
        "Общаться, отвечать на вопросы, поддержать 🙂 Что интересует?",
        "Много чего — рассказать анекдот, поиграть, поболтать 🙂",
    ],
    "можешь": [
        "Много чего 🙂 Рассказать анекдот, поиграть, поболтать 🙂",
        "Могу поговорить, поиграть, ответить на вопросы 🙂",
        "Всё, что угодно 🙂 Что хочешь?",
    ],
    "помочь": ["Конечно 🙂 Расскажи, что нужно", "Попробую 🙂 В чём вопрос?"],
    "help": ["Слушаю 🙂 Что нужно?", "Помогу чем смогу 🙂"],
    "помоги": ["Расскажи, что случилось 🙂", "Слушаю 🙂"],
    "функци": ["Команды: /mode /mood /invite /joke /dice /coin /evil /good /reset 🙂"],
    "команд": ["Команды: /mode /mood /invite /joke /dice /coin /evil /good /reset 🙂"],
    "извини": ["Да ладно, проехали 🙂", "Всё ок!", "Ничего страшного 🙂", "Забыли!"],
    "прости": ["Да ладно, всё норм 🙂", "Забыли!", "Ничего 🙂", "Да брось, ерунда!"],
    "сорри": ["Ок, проехали 🙂", "Ничего страшного!", "Да ладно 🙂"],
    "sorry": ["Всё ок 🙂", "Забыли!", "Да не парься 🙂"],
    "виноват": ["Да ладно, все мы люди 🙂", "Ничего, бывает!", "Проехали 🙂"],
    "прощаешь": ["Конечно 🙂", "Да ладно, не парься!", "Всё ок!", "Куда я денусь 😄"],
    "простишь": ["Конечно 🙂", "Да ладно, всё норм!", "Ага, проехали 🙂"],
    "мир": ["Мир 🤝", "Мир-мир 🙂", "Ок, мир! ✌️"],
    "мириться": ["Давай 🙂", "Мир-мир!", "Ок, я не злопамятный 🙂"],
    "помирились": ["Ура! 🎉", "Вот и отлично 🙂", "Мир-мир ✌️"],
    "не обижайся": ["Да не обижаюсь я 🙂", "Всё ок!", "Да брось 🙂"],
    "не сердись": ["Да не сержусь 🙂", "Всё норм!", "Ок 🙂"],
    "как день": ["Норм 🙂 А у тебя?", "Хорошо! Ты как?", "Отлично 🙂 Как сам?"],
    "как прошёл день": ["Норм 🙂 А у тебя?", "Хорошо прошёл! Ты как?", "Отлично 🙂"],
    "что делал": ["Да так, отдыхал 🙂 Ты чем занят?", "Ничего особенного. Ты что делал?"],
    "что нового": ["Да всё по-старому 🙂 А у тебя?", "Новостей особо нет. Ты что?"],
    "как успехи": ["Отлично 🙂 А у тебя?", "Всё хорошо! Как сам?", "Норм 🙂"],
    "что кушал": ["О, вкусно поел 🙂 А ты?", "Да так, перекусил. Ты что ел?", "Ням-ням 😋"],
    "что ел": ["О, вкусно поел 🙂 А ты?", "Перекусил. Ты что?", "Ням 😋"],
    "что слушаешь": ["Что-то спокойное 🙂 А ты?", "Разное. Ты что слушаешь?"],
    "как спалось": ["Отлично 🙂 А ты как?", "Хорошо выспался! Ты как?", "Норм 🙂"],
    "доброе утро": ["Доброе утро! ☀️ Как спалось?", "Утро доброе 🙂 Выспался?"],
    "спокойной ночи": ["Спокойной ночи 🌃 Сладких снов", "Спокойной ночи! 😴 Спи хорошо"],
    "спать хочу": ["Иди спать 😴 Спокойной ночи!", "Отдыхай, я тут посижу 🙂"],
    "пошли спать": ["Ладно, пошли спать, спокойной ночи 😴🌃", "Пошли 😴 Спокойной ночи!"],
    "как ты": ["Отлично 🙂 А ты как?", "Всё хорошо! Ты как?"],
    "чем занят": ["Да болтаю с тобой 🙂 А ты?", "Ничем особенным. Ты что делаешь?"],
}

NEUTRAL_GOOD = [
    "Понял 🙂", "Хм, интересно", "Расскажи ещё", "И что дальше?",
    "Прикольно!", "А что было потом?", "Согласен 🙂", "Действительно",
    "Интересно 🤔", "Понимаю", "Ого!", "Ничего себе!",
]

SHORT_GOOD = ["ага", "ну да", "хм", "ок)", "понял", "ясно", "ага-ага"]

TOPICS_EVIL = {
    "привет": ["О, ты. Чего надо?", "Ну привет. Чё хотел?"],
    "как дела": ["Лучше всех. А тебе какое дело?", "Норм. Тебе-то что?"],
    "что делаешь": ["Да вот, тебя слушаю. Скукота."],
    "люблю тебя": ["Ага, конечно.", "Не льсти себе."],
    "ты кто": ["Тот, кто умнее тебя.", "Не твоё дело."],
    "скучно": ["Ну так займись чем-нибудь.", "Иди уроки делай."],
    "мем": ["Свои мемы кидай, тут не цирк."],
    "аниме": ["Аниме? Взрослей уже."],
    "школа": ["Школа? Ну удачи, двоечник."],
    "игр": ["Опять игры. Книгу открой."],
    "работа": ["Работа? Ха. Хоть что-то делаешь."],
    "умеешь": ["Много чего. Но тебе не скажу.", "Тебе не нужно знать."],
    "можешь": ["Могу. Но не хочу."],
    "извини": ["Ладно, прощаю. В этот раз.", "Хм. Ладно, живи."],
    "прости": ["Ладно. Но ты мне должен 😏", "Хм, ну ок."],
}
NEUTRAL_EVIL = ["Ну и что?", "И чё?", "Дальше что?", "Ясно."]
SHORT_EVIL = ["ага", "ясно", "ну-ну", "и чё", "ок"]

SAD_WORDS = ["плохо", "устал", "грустно", "печально", "тяжело", "депресс", "не могу больше"]
HAPPY_WORDS = ["круто", "ура", "класс", "супер", "отлично", "здорово", "кайф"]


def has_bad_word(text):
    t = text.lower()
    return any(w in t for w in BAD_WORDS)


def has_fear(text):
    t = text.lower()
    return any(w in t for w in FEAR_WORDS)


def has_sad(text):
    t = text.lower()
    return any(w in t for w in SAD_WORDS)


def has_happy(text):
    t = text.lower()
    return any(w in t for w in HAPPY_WORDS)


def build_reply(text, mode, history, name, mood, last_action):
    t = text.lower().strip()
    h_now = datetime.now().hour
    is_night = (h_now >= 22 or h_now < 6)

    # ==== ГРУБОСТЬ ====
    if has_bad_word(text):
        return random.choice(COUNTER_ATTACKS)

    # ==== НОЧЬ — СНАЧАЛА ПОДДЕРЖКА ====
    if is_night and mode == "good":
        if has_fear(text):
            return random.choice([
                "Я тут 🫂 Не бойся, всё хорошо",
                "Расскажи, что случилось? Я слушаю",
                "Всё нормально, я рядом 🙂",
                "Не бойся, я тут. Что тебя тревожит?",
                "Дыши глубже. Я тут, всё ок 🫂",
                "Давай поговорим, я никуда не уйду 🙂",
                "Ты не один. Я тут 🫂",
                "Всё будет хорошо. Расскажи, что не так?",
                "Не бойся. Хочешь, поговорим? 🙂",
                "Я с тобой. Что тревожит? 🫂",
            ])

    # ==== «СПОКОЙНОЙ НОЧИ» ====
    if "спокойной ночи" in t or "пошли спать" in t:
        if mode == "good":
            return "Ладно, пошли спать, спокойной ночи 😴🌃"

    # ==== АНЕКДОТ ====
    if "анекдот" in t or ("расскаж" in t and last_action == "joke_offer"):
        return "🎭 " + random.choice(JOKES)

    # ==== ИГРЫ ====
    if "кубик" in t or "кости" in t:
        return f"🎲 Выпало: {random.randint(1, 6)}"
    if "монетка" in t or "монету" in t:
        return f"🪙 {random.choice(['Орёл!', 'Решка!'])}"
    if "угадай число" in t or "угадать число" in t:
        return "Загадал число от 1 до 100! Пиши свои догадки 🤔"
    if "магический шар" in t or ("шар" in t and len(t) < 30):
        return f"🔮 {random.choice(['Да', 'Нет', 'Может быть', 'Спроси позже', 'Определённо да', 'Определённо нет'])}"

    # ==== ГРУСТЬ ====
    if has_sad(text) and mode == "good":
        return random.choice([
            "Что случилось? Расскажи, если хочешь 🫂",
            "Оу... хочешь поговорить об этом?",
            "Бывает. Может, чайку и отдохнуть? ☕",
            "Печально. Я тут, если что 🙂",
        ])

    # ==== РАДОСТЬ ====
    if has_happy(text) and mode == "good":
        return random.choice([
            "О, круто! 🎉", "Рад за тебя!", "Молодец!", "Супер! 😄",
        ])

    if mode == "evil":
        topics = TOPICS_EVIL
        neutral = NEUTRAL_EVIL
        short = SHORT_EVIL
    else:
        topics = TOPICS_GOOD
        neutral = NEUTRAL_GOOD
        short = SHORT_GOOD

    forgiveness_keys = ["извини", "прости", "сорри", "sorry", "виноват",
                        "прощаешь", "простишь", "мир", "мириться",
                        "помирились", "не обижайся", "не сердись"]
    for k in forgiveness_keys:
        if k in t and k in topics:
            return random.choice(topics[k])

    ability_keys = ["умеешь", "можешь", "помочь", "help", "помоги",
                    "функци", "команд"]
    for k in ability_keys:
        if k in t and k in topics:
            return random.choice(topics[k])

    for k, v in topics.items():
        if k in t:
            return random.choice(v)

    if len(t) <= 4:
        return random.choice(short)

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
        ])

    if is_night and mode == "good" and random.random() < 0.10:
        return random.choice([
            "Ты чего не спишь? 🌚 Если что — я тут",
            "Поздно уже. Но если хочешь поговорить — давай 🙂",
            "Может, спать? Но я тут, если что 🙂",
        ])

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
        "/joke — анекдот\n/dice — кубик\n/coin — монетка\n"
        "/evil — злой (после 3 приглашений)\n/good — добрый\n/reset — сброс")


@bot.message_handler(commands=["mood"])
def cmd_mood(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    mood = user.get("mood", "calm")
    save_data(data)
    moods_ru = {"happy": "😊 радостный", "calm": "🙂 спокойный",
                "sad": "😔 грустный", "sleepy": "😴 сонный", "thoughtful": "🤔 задумчивый"}
    bot.send_message(m.chat.id, f"Сейчас настроение: {moods_ru.get(mood, '🙂')}")


@bot.message_handler(commands=["joke"])
def cmd_joke(m):
    bot.send_message(m.chat.id, "🎭 " + random.choice(JOKES))


@bot.message_handler(commands=["dice"])
def cmd_dice(m):
    bot.send_message(m.chat.id, f"🎲 Выпало: {random.randint(1, 6)}")


@bot.message_handler(commands=["coin"])
def cmd_coin(m):
    bot.send_message(m.chat.id, f"🪙 {random.choice(['Орёл!', 'Решка!'])}")


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
    bot.send_message(m.chat.id, f"Твоя ссылка:\n{link}\n\nПриглашено: {invited}/3\nОсталось: {need}")


@bot.message_handler(commands=["evil"])
def cmd_evil(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    if not user.get("evil_unlocked", False):
        invited = len(user.get("invited", []))
        save_data(data)
        bot.send_message(m.chat.id, f"Злой режим пока закрыт 🔒\n\nПриглашено: {invited}/3\n/invite")
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

    # ==== В ГРУППАХ — ОТВЕЧАЕМ ТОЛЬКО ЕСЛИ ОБРАТИЛИСЬ ====
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        mentioned = False
        if m.entities:
            for entity in m.entities:
                if entity.type == "mention":
                    mention_text = m.text[entity.offset:entity.offset + entity.length]
                    if mention_text.lower() == "@" + bot.get_me().username.lower():
                        mentioned = True
                        break
        if not reply_to_bot and not mentioned:
            return

    data = load_data()
    user = get_user(data, m.from_user.id)
    mode = user.get("mode", "good")
    name = user.get("name", "") or m.from_user.first_name or "друг"
    last_action = user.get("last_action", "")

    user["msg_count"] = user.get("msg_count", 0) + 1
    if user["msg_count"] % 12 == 0:
        user["mood"] = random.choice(MOODS)
    if user["mood"] not in MOODS:
        user["mood"] = mood_from_time()

    mood = user["mood"]
    reply = build_reply(m.text, mode, user.get("history", []), name, mood, last_action)

    if "анекдот" in reply.lower() and "?" in reply:
        user["last_action"] = "joke_offer"
    else:
        user["last_action"] = ""

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
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, random.choice(
        ["О, стикер! 🙂", "Классный 😄", "Хм, интересный", "Прикольно!", "👍", "Ахах 😄"]))


@bot.message_handler(content_types=["photo"])
def on_photo(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, random.choice(
        ["О, фото! 📸", "Красиво!", "Что это?", "Классный кадр 🙂", "Прикольное фото!"]))


@bot.message_handler(content_types=["video"])
def on_video(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, random.choice(["О, видео! 🎬", "Что там?", "Интересно 🙂"]))


@bot.message_handler(content_types=["voice"])
def on_voice(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, random.choice(["О, голосовое 🎤", "Что говоришь?", "Слушаю 🙂"]))


@bot.message_handler(content_types=["document"])
def on_document(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, "О, документ 📄 Спасибо!")


@bot.message_handler(content_types=["audio"])
def on_audio(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, "О, музыка 🎵 Что слушаешь?")


@bot.message_handler(content_types=["animation"])
def on_gif(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        reply_to_bot = (
            m.reply_to_message and
            m.reply_to_message.from_user and
            m.reply_to_message.from_user.id == bot.get_me().id
        )
        if not reply_to_bot:
            return
    bot.send_message(m.chat.id, "О, гифка! 😄")


@bot.message_handler(func=lambda m: True)
def other(m):
    is_group = m.chat.type in ["group", "supergroup"]
    if is_group:
        return
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
