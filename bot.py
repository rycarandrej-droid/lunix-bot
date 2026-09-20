import telebot
import random
import time
import threading
import json
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")
print(f"DEBUG: OPENROUTER_KEY length = {len(OPENROUTER_KEY)}, starts with = {OPENROUTER_KEY[:15]}")
print(f"DEBUG: BOT_TOKEN length = {len(BOT_TOKEN)}, starts with = {BOT_TOKEN[:15]}")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-8b-instruct:free"

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
            "invited": [],
            "evil_unlocked": False,
            "history": [],
            "name": ""
        }
    if "history" not in data[uid]:
        data[uid]["history"] = []
    if "name" not in data[uid]:
        data[uid]["name"] = ""
    return data[uid]


BAD_WORDS = [
    "дурак", "идиот", "тупой", "лох ", "дебил", "козёл", "козел",
    "придурок", "чмо", "кретин", "додик", "олух", "болван",
    "тупица", "бестолочь", "недоумок", "баран", "осёл", "осел",
    "хам", "наглец", "нахал", "клоун", "дегенерат", "имбецил",
    "мразь", "тварь", "гнида", "падла", "сволочь", "мерзавец",
    "подлец", "негодяй", "паразит", "отморозок", "лошара",
    "чмошник", "сопляк", "ничтожество", "нищеброд", "гопник",
    "быдло", "быдлан",
    "нахуй", "нахуя", "похуй", "охуел", "охуеть", "ахуел",
    "заебал", "заебись", "отъебись", "хуй", "хуя", "хую", "хуё",
    "пизд", "пиздец", "блядь", "бляди", "блят",
    "ебал", "ебан", "ебать", "ебуч", "ёбал", "ёбан", "ёбать",
    "сука", "суки", "сучка", "мудак", "мудила", "гандон", "гондон",
    "шлюха", "дрочи", "залупа", "пидор", "пидар", "педик",
    "долбоёб", "долбоеб", "жопа", "говно", "говнюк",
    "хуесос", "педофил",
]

COUNTER_ATTACKS = [
    "Ой, как грубо 😏",
    "Сам иди, я тут посижу",
    "Смело. Только неэффективно 🙃",
    "Так-так, кто-то не в настроении",
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
    "Как мило. Мне очень важно твоё мнение. Нет.",
    "Похоже, кто-то не выспался сегодня.",
    "Серьёзно? Это всё, что ты можешь?",
    "Да ладно, ты серьёзно? 😂",
    "Ты чего такой злой? Обними кого-нибудь 🫂",
    "Хм, интересно. Мне всё равно, но интересно.",
    "Ну и характер. Тебе бы в цирке работать 🎪",
]


def has_bad_word(text):
    t = text.lower()
    for word in BAD_WORDS:
        if word in t:
            return True
    return False


def ask_ai(user_message, user_name, mode, history):
    if not OPENROUTER_KEY:
        print("DEBUG: ask_ai called, but OPENROUTER_KEY is EMPTY")
        return None

    print(f"DEBUG: ask_ai sending request, key starts with {OPENROUTER_KEY[:10]}")

    if mode == "evil":
        system = (
            f"Ты — саркастичный, язвительный собеседник. Тебя зовут Lunixz. "
            f"Собеседника зовут {user_name or 'друг'}. "
            f"Отвечай коротко (1-2 предложения), с сарказмом, но без мата и без угроз. "
            f"Не признавайся, что ты бот или AI. Говори как человек."
        )
    else:
        system = (
            f"Ты — дружелюбный собеседник. Тебя зовут Lunixz. "
            f"Собеседника зовут {user_name or 'друг'}. "
            f"Отвечай коротко (1-2 предложения), по-дружески, живо. "
            f"Не признавайся, что ты бот или AI. Говори как человек."
        )

    messages = [{"role": "system", "content": system}]
    for h in history[-6:]:
        messages.append(h)
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.9,
            },
            timeout=25,
        )
        print(f"DEBUG: OpenRouter response status = {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            print(f"AI error: {response.status_code} — {response.text[:200]}")
            return None
    except Exception as e:
        print(f"AI exception: {e}")
        return None


TOPICS_GOOD = {
    "привет": ["Привет!", "О, привет 🙂", "Привет-привет!", "Хай ✌️"],
    "как дела": ["Да норм, а ты?", "Всё хорошо 🙂 ты как?", "Отлично! А у тебя?"],
    "люблю тебя": ["И я тебя ❤️", "Ты самый лучший 🙂", "Обнимаю 🤗"],
    "ты кто": ["Твой друг 🙂", "Просто человек"],
    "скучно": ["Расскажу анекдот?", "Давай поиграем"],
    "мем": ["Кидай мем 🙂", "О, мемы — топ!"],
    "python": ["О, программист 🐍"],
}
NEUTRAL_GOOD = ["Понял 🙂", "Хм, интересно", "Расскажи ещё"]
SHORT_GOOD = ["ага", "ну да", "хм", "ок)", "понял"]


def fallback_reply(text):
    t = text.lower().strip()
    for k, v in TOPICS_GOOD.items():
        if k in t:
            return random.choice(v)
    if len(t) <= 4:
        return random.choice(SHORT_GOOD)
    return random.choice(NEUTRAL_GOOD)


@bot.message_handler(commands=["start"])
def cmd_start(m):
    data = load_data()
    user = get_user(data, m.from_user.id)
    user["name"] = m.from_user.first_name or ""
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
    bot.send_message(m.chat.id,
        f"Привет, {name}! 👋\n\nЯ Lunixz — просто собеседник 🙂\n\n"
        "Команды:\n/mode — режим\n/invite — пригласить друзей\n"
        "/evil — злой (после 3 приглашений)\n/good — добрый\n/reset — сбросить память")


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

    if has_bad_word(m.text):
        reply = random.choice(COUNTER_ATTACKS)
        save_data(data)
        time.sleep(1)
        bot.send_message(m.chat.id, reply)
        return

    bot.send_chat_action(m.chat.id, "typing")
    time.sleep(random.uniform(1, 3))

    ai_reply = ask_ai(m.text, name, mode, user.get("history", []))
    if not ai_reply:
        ai_reply = fallback_reply(m.text)

    user["history"].append({"role": "user", "content": m.text})
    user["history"].append({"role": "assistant", "content": ai_reply})
    user["history"] = user["history"][-10:]
    save_data(data)

    bot.send_message(m.chat.id, ai_reply)


@bot.message_handler(content_types=["sticker"])
def on_sticker(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, стикер! 🙂", "Классный 😄", "Хм, интересный", "Прикольно!", "👍"]))


@bot.message_handler(content_types=["photo"])
def on_photo(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, фото! 📸", "Красиво!", "Что это?", "Классный кадр 🙂", "Прикольное фото!"]))


@bot.message_handler(content_types=["video"])
def on_video(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, видео! 🎬", "Что там?", "Интересно 🙂"]))


@bot.message_handler(content_types=["voice"])
def on_voice(m):
    bot.send_message(m.chat.id, random.choice(
        ["О, голосовое 🎤", "Что говоришь?", "Слушаю 🙂"]))


@bot.message_handler(content_types=["document"])
def on_document(m):
    bot.send_message(m.chat.id, "О, документ 📄 Спасибо!")


@bot.message_handler(content_types=["audio"])
def on_audio(m):
    bot.send_message(m.chat.id, "О, музыка 🎵")


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
