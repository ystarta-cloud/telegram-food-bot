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

# -------- МЕНЮ --------

menu = {

    "🥗 Салаты": {
        "Оливье": 3,
        "Винегрет": 3,
        "Греческий": 4,
        "Цезарь с курицей": 5
    },

    "🍲 Первые блюда": {
        "Борщ": 4,
        "Куриный суп": 3,
        "Солянка": 5
    },

    "🍖 Горячее": {
        "Котлеты домашние": 5,
        "Плов": 6,
        "Курица в духовке": 6
    },

    "🍚 Гарниры": {
        "Картофельное пюре": 3,
        "Рис": 2,
        "Гречка": 2
    },

    "🍽 Готовый ужин": {
        "🚚 Доставка": 0,
        "🛒 Что-то купим": 0,
        "🌆 Сходим куда-то": 0
    }
}

carts = {}
comments = {}
waiting_comment = set()

# -------- КНОПКА СТАРТА --------

def welcome_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🍽 Начать заказ"))
    return kb

# -------- ГЛАВНОЕ МЕНЮ --------

def main_menu():
    kb = InlineKeyboardMarkup()
    for cat in menu:
        kb.add(InlineKeyboardButton(cat, callback_data=f"cat|{cat}"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))
    return kb

# -------- КАТЕГОРИЯ --------

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

# -------- START --------

@bot.message_handler(commands=["start"])
def start(message):
    carts[message.chat.id] = {}

    bot.send_message(
        message.chat.id,
        "🏡 *Домашняя кухня*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=welcome_keyboard()
    )

# -------- НАЧАТЬ --------

@bot.message_handler(func=lambda m: m.text == "🍽 Начать заказ")
def open_menu(message):
    carts[message.chat.id] = {}

    bot.send_message(
        message.chat.id,
        "🍲 *Наше меню*",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# -------- CALLBACK --------

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

        if dish in ["🚚 Доставка", "🛒 Что-то купим", "🌆 Сходим куда-то"]:
            carts[user] = {dish: 1}
            bot.send_message(user, "💬 Напишите комментарий к заказу")
            waiting_comment.add(user)
            return

        carts.setdefault(user, {})
        carts[user][dish] = carts[user].get(dish, 0) + 1
        bot.answer_callback_query(call.id, "Добавлено 🤗")

    elif data == "back":
        bot.edit_message_text(
            "🍲 Меню:",
            user,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "cart":
        show_cart(call.message)

    elif data.startswith("plus|"):
        dish = data.split("|")[1]
        carts[user][dish] += 1
        show_cart(call.message)

    elif data.startswith("minus|"):
        dish = data.split("|")[1]
        carts[user][dish] -= 1
        if carts[user][dish] <= 0:
            del carts[user][dish]
        show_cart(call.message)

    elif data == "order":
        send_order(call.message)

    elif data == "comment":
        waiting_comment.add(user)
        bot.send_message(user, "Напишите комментарий 💬")

# -------- ЦЕНА --------

def find_price(dish):
    for cat in menu.values():
        if dish in cat:
            return cat[dish]
    return 0

# -------- КОРЗИНА --------

def show_cart(message):
    user = message.chat.id
    cart = carts.get(user, {})

    if not cart:
        bot.send_message(user, "Корзина пустая 😢")
        return

    text = "🛒 Ваша корзина:\n\n"
    total = 0
    kb = InlineKeyboardMarkup()

    for dish, qty in cart.items():
        price = find_price(dish)
        total += price * qty

        text += f"{dish} x{qty} = {price*qty} 💋\n"

        kb.add(
            InlineKeyboardButton("➖", callback_data=f"minus|{dish}"),
            InlineKeyboardButton("➕", callback_data=f"plus|{dish}")
        )

    text += f"\nИТОГО: {total} 🤗"

    kb.add(InlineKeyboardButton("💬 Комментарий", callback_data="comment"))
    kb.add(InlineKeyboardButton("✅ Оформить заказ", callback_data="order"))

    bot.send_message(user, text, reply_markup=kb)

# -------- ЗАКАЗ --------

def send_order(message):
    user = message.chat.id
    cart = carts.get(user, {})

    total = 0
    text = "🔥 Новый заказ:\n\n"

    for dish, qty in cart.items():
        price = find_price(dish)
        total += price * qty
        text += f"{dish} x{qty}\n"

    comment = comments.get(user, "нет")
    text += f"\n💬 Комментарий: {comment}"
    text += f"\n\nИТОГО: {total} 💋"

    bot.send_message(ADMIN_ID, text)
    bot.send_message(user, "✅ Заказ отправлен ❤️")

    carts[user] = {}

# -------- КОММЕНТАРИЙ --------

@bot.message_handler(func=lambda m: m.chat.id in waiting_comment)
def get_comment(message):
    user = message.chat.id

    comments[user] = message.text
    waiting_comment.remove(user)

    bot.send_message(user, "💌 Комментарий сохранён!")

# -------- ЗАПУСК --------

print("Бот запущен ❤️")
bot.infinity_polling(none_stop=True)
