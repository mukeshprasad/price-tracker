import os
import time
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from threading import Thread
from controller import Controller
from constants import INTRO_MESSAGE


BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") or "<ENTER_YOUR_TOKEN_HERE>"
bot = telebot.TeleBot(BOT_TOKEN)


def create_untrack_keyboard(product_ids):
    keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    for product_id in range(1, product_ids + 1, 2):
        row = []
        for j in range(2):
            if product_id + j <= product_ids:
                button_text = f"/untrack_{product_id + j}"
                row.append(KeyboardButton(button_text))
        keyboard.row(*row)
        # keyboard.add(KeyboardButton(button_text))
    return keyboard


@bot.message_handler(commands=["start", "hello", "hi", "help"])
def send_welcome(message):
    bot.reply_to(message, INTRO_MESSAGE)


@bot.message_handler(commands=["list"])
def send_tracking_list(message):
    count, response = Controller.get_tracking_list(message)
    disable_preview = False
    if count > 1:
        disable_preview = True
    bot.reply_to(message, response, disable_web_page_preview=disable_preview)


@bot.message_handler(commands=["untrack"])
def untrack_product(message):
    user_id = message.from_user.id
    count = Controller.tracking_list_count(message)
    if count in [0, None]:
        bot.reply_to(message, "You are not tracking any products.")
    else:
        bot.reply_to(
            message,
            "You can untrack a product, using the below command.\n/untrack_<id>",
        )
        keyboard = create_untrack_keyboard(count)
        bot.reply_to(message, "Select a product to untrack:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.startswith("/untrack_"))
def handle_untrack_product(message):
    response = Controller.untrack_product(message)
    bot.reply_to(message, response, reply_markup=ReplyKeyboardRemove())


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    user_id = message.from_user.id
    response = Controller.run(message)
    bot.reply_to(message, response)


def track_and_send_msg():
    while True:
        response = Controller.get_tracker_response(bot)
        time.sleep(120)


tracker = Thread(target=track_and_send_msg, daemon=True)
tracker.start()

# bot.infinity_polling(restart_on_change=True)
bot.infinity_polling()
