"""
В данном файле описывается работа с ботом Телеграм
"""
import telebot
from . import messages as msg
from . import tg_bot_token
from .extensions import CBRApi


bot = telebot.TeleBot(tg_bot_token.TG_BOT_TOKEN)
api = CBRApi()


def get_bot():
    return bot


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, msg.HELP_MESSAGE)


@bot.message_handler(commands=['usage'])
def handle_help(message):
    bot.send_message(message.chat.id, msg.QUERY_FORMAT)


@bot.message_handler(commands=['values'])
def handle_values(message):
    currencies_list = api.get_currencies_list()
    values_msg = msg.get_values_message(currencies_list)
    bot.send_message(message.chat.id, values_msg)


@bot.message_handler(commands=['start'])
def handle_message(message):
    start_message = msg.get_start_message(message.from_user.full_name)
    bot.send_message(message.chat.id, f'{start_message}\n{msg.HELP_MESSAGE}')


@bot.message_handler(content_types='text')
def handle_query(message):
    res = api.get_price(message.text.upper())
    bot.send_message(message.chat.id, res, parse_mode='Markdown')
