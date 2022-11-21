import src.telegram as tg


def main():
    bot = tg.get_bot()
    print('Бот получен. Запущен.')
    bot.infinity_polling()


if __name__ == '__main__':
    main()
