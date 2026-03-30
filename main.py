import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

TOKEN = "8744591042:AAFyj7PlRxAno2lWLhTkaQp6rbO1toEuatM"
ADMIN_ID = 5781019834

bot = telebot.TeleBot(TOKEN)

# ---------------- МЕНЮ ----------------

menu = {

    "🥗 Салаты": {
        "Оливье":3,"Винегрет":3,"Греческий":4,"Цезарь с курицей":5,
        "Цезарь с креветками":6,"Крабовый салат":4,"Салат с курицей и грибами":5,
        "Салат с ветчиной и сыром":4,"Свекольный с чесноком":3,
        "Морковь по-корейски":3,"Капустный салат":2,"Овощной салат":3,
        "Салат с фасолью":3,"Селёдка под шубой":5,"Мимоза":5,
        "Салат с копчёной курицей":5,"Салат с авокадо":6,
        "Салат с яйцом и огурцом":3
    },

    "🍲 Первые блюда": {
        "Борщ":4,"Куриный суп с лапшой":3,"Суп с фрикадельками":4,
        "Гороховый суп":3,"Рассольник":4,"Солянка":5,
        "Сырный суп":4,"Грибной суп":4,"Овощной суп":3,
        "Крем-суп грибной":5,"Уха":6,"Харчо":5,
        "Суп с рисом и курицей":4,"Картофельный суп":3,
        "Суп с фасолью":4,"Лёгкий куриный бульон":3
    },

    "🍖 Горячее": {
        "Котлеты домашние":5,"Куриные котлеты":5,"Тефтели в соусе":5,
        "Голубцы":6,"Ленивые голубцы":5,"Плов":6,
        "Курица в духовке":6,"Куриные ножки запечённые":6,
        "Курица в сливочном соусе":7,"Отбивные свиные":7,
        "Фаршированные перцы":6,"Скумбрия в духовке":7,
        "Лосось запечённый":9,"Овощное рагу":4,
        "Картофельная запеканка":5,"Паста с курицей":6,
        "Лазанья":7,"Рис с курицей":5
    },

    "🍚 Гарниры": {
        "Картофельное пюре":3,"Жареный картофель":3,
        "Картофель по-деревенски":4,"Картофель запечённый":4,
        "Рис отварной":2,"Рис с овощами":3,"Гречка":2,
        "Булгур":3,"Макароны":2,"Спагетти":3,
        "Тушёная капуста":3,"Овощи на пару":4,
        "Запечённые овощи":4,"Фасоль тушёная":3,
        "Чечевица":3,"Перловка":2,
        "Цветная капуста запечённая":4
    },

    "🥟 Блюда из теста": {
        "Пельмени":5,"Вареники с картошкой":4,"Вареники с творогом":4,
        "Вареники с вишней":5,"Манты":6,"Хинкали":6,
        "Домашняя пицца":7,"Лаваш с сыром":4,
        "Лаваш с курицей":5,"Блины":3,"Оладьи":3,
        "Сырники":4,"Хачапури":6,
        "Пирожки с картошкой":3,"Пирожки с капустой":3,
        "Пирог с мясом":6,"Киш с курицей":6
    },

    "🍰 Десерты": {
        "Шарлотка":4,"Медовик":5,"Наполеон":5,
        "Чизкейк":6,"Творожная запеканка":4,
        "Сырники сладкие":4,"Блины сладкие":3,
        "Желе фруктовое":3,"Десерт из творога":4,
        "Банановый десерт":4,"Шоколадный мусс":5,
        "Пирог с яблоками":4
    },

    "⚡ Быстрые блюда": {
        "Омлет":3,"Яичница":2,"Омлет с сыром":3,
        "Горячие бутерброды":3,"Лаваш с начинкой":4,
        "Шаурма домашняя":5,"Паста с сыром":4,
        "Сосиски с гарниром":4,"Жареные пельмени":5,
        "Быстрая пицца на лаваше":4,"Тосты с яйцом":3,
        "Картофель на сковороде":3,"Сэндвич с курицей":5,
        "Творог с фруктами":4
    },

    "🍽 Готовый ужин": {
        "🚚 Доставка":0,
        "🛒 Что-то купим":0,
        "🌆 Сходим куда-то":0
    }
}

carts = {}
comments = {}
waiting_comment = set()

# ---------- КНОПКИ ----------

def welcome_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🍽 Начать заказ"))
    return kb

def main_menu():
    kb = InlineKeyboardMarkup()
    for cat in menu:
        kb.add(InlineKeyboardButton(cat, callback_data=f"cat|{cat}"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))
    return kb

def category_menu(cat):
    kb = InlineKeyboardMarkup()
    for dish, price in menu[cat].items():
        kb.add(
            InlineKeyboardButton(
                f"{dish} — {price} 🤗",
                callback_data=f"add|{dish}"
            )
        )
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return kb

# ---------- START ----------

@bot.message_handler(commands=["start"])
def start(message):
    carts[message.chat.id] = {}
    bot.send_message(
        message.chat.id,
        "🏡 Домашняя кухня ❤️",
        reply_markup=welcome_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🍽 Начать заказ")
def open_menu(message):
    bot.send_message(
        message.chat.id,
        "🍲 Выберите категорию:",
        reply_markup=main_menu()
    )

# ---------- CALLBACK ----------

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user = call.message.chat.id
    data = call.data

    if data.startswith("cat|"):
        cat = data.split("|")[1]
        bot.edit_message_text(
            f"📂 {cat}",
            user,
            call.message.message_id,
            reply_markup=category_menu(cat)
        )

    elif data.startswith("add|"):
        dish = data.split("|")[1]

        if dish in menu["🍽 Готовый ужин"]:
            carts[user] = {dish:1}
            waiting_comment.add(user)
            bot.send_message(user,"💬 Напишите комментарий")
            return

        carts.setdefault(user,{})
        carts[user][dish]=carts[user].get(dish,0)+1
        bot.answer_callback_query(call.id,"Добавлено 🤗")

    elif data=="back":
        bot.edit_message_text(
            "🍲 Меню:",
            user,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif data=="cart":
        show_cart(call.message)

    elif data=="order":
        send_order(call.message)

# ---------- ВСПОМОГАТЕЛЬНОЕ ----------

def find_price(dish):
    for cat in menu.values():
        if dish in cat:
            return cat[dish]
    return 0

def show_cart(message):
    user=message.chat.id
    cart=carts.get(user,{})

    if not cart:
        bot.send_message(user,"Корзина пустая 😢")
        return

    text="🛒 Корзина:\n\n"
    total=0

    for dish,qty in cart.items():
        price=find_price(dish)
        total+=price*qty
        text+=f"{dish} x{qty} = {price*qty} 💋\n"

    text+=f"\nИТОГО: {total} 🤗"

    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💬 Комментарий",callback_data="comment"))
    kb.add(InlineKeyboardButton("✅ Оформить заказ",callback_data="order"))

    bot.send_message(user,text,reply_markup=kb)

def send_order(message):
    user = message.chat.id
    username = message.from_user.first_name

    cart = carts.get(user, {})
    total = 0

    text = (
        "🍽 НОВЫЙ ДОМАШНИЙ ЗАКАЗ\n"
        "━━━━━━━━━━━━━━━\n"
    )

    for dish, qty in cart.items():
        price = find_price(dish)
        total += price * qty
        text += f"🍴 {dish} × {qty}\n"

    text += f"\n💰 Итого: {total} 🤗"

    comment = comments.get(user, "нет")
    text += f"\n💬 Комментарий: {comment}"

    text += (
        "\n━━━━━━━━━━━━━━━\n"
        f"👤 Клиент: {username}\n"
        f"🆔 ID: {user}"
    )

    # кнопка ответа клиенту
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "💬 Написать клиенту",
            url=f"tg://user?id={user}"
        )
    )

    bot.send_message(ADMIN_ID, text, reply_markup=kb)
    bot.send_message(user, "✅ Заказ отправлен ❤️")

    carts[user] = {}

@bot.message_handler(func=lambda m: m.chat.id in waiting_comment)
def get_comment(message):
    comments[message.chat.id]=message.text
    waiting_comment.remove(message.chat.id)
    bot.send_message(message.chat.id,"Комментарий сохранён ❤️")

print("Бот запущен ❤️")
bot.infinity_polling(none_stop=True)
