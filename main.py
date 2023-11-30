"""
Воронка начинается после первого сообщения от клиента.
Пояснение: бот проверяет есть ли человек в БД, и если нет, то регистрирует его в БД и начинается воронка
Через какое время:
Сообщения, которые отправляет с момента последнего
через 10 минут	Добрый день!
через 90 минут	Подготовила для вас материал
Сразу после	Отправка любого фото
Через 2 часа, если не найден в истории сообщений триггер "Хорошего дня" (от лица нашего аккаунта)
Скоро вернусь с новым материалом!
ЯП -- python. Использовать sqlalchemy (asyncpg) - для БД, pyrogram - для взаимодействия с Telegram API.
Логировать каждую успешную отправку сообщения с помощью loguru.
Сделать возможность просмотра кол-во зарегистрированный людей в БД за сегодня с помощью отправки команды
/users_today в избранное аккаунта.
Использовать person telegram.
"""
import asyncio
from time import sleep
from loguru import logger
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from connect_db import insert_db, view_user

api_id = 000  # Добавить свой id и hash
api_hash = ''
data_auth = []
check_admin = False

client = Client(name='me_client', api_id=api_id, api_hash=api_hash)
with Client(name='me_client', api_id=api_id, api_hash=api_hash) as app:
    app.send_message("me", "Введите логин и пароль через Enter")

    @client.on_message()
    def log(client, message):
        """Получаем от пользователя введенный логи и пароль, а затем вызываем функцию insert_db."""
        print(message)
        logger.add("file.log", enqueue=True)
        data_auth.append(message.text)
        if len(data_auth) > 1:
            asyncio.run(insert_db(data_auth))
            client.stop()
            if data_auth[0] == 'admin' and data_auth[1] == 'admin':  # FIXME этот вариант проверки не безопасен.
                global check_admin
                check_admin = True

    # sleep(600)
    app.send_message("me", "Добрый день!")
    # sleep(5400)
    app.send_message("me", "Подготовила для Вас материал")
    app.send_photo("me", "C:/Users/Bjj/Documents/Каюга.png", caption='<b> Фото </b>')

    # sleep(7200)
    async def filter_text(_, __, message):
        """Проверка триггера хорошего дня."""
        return message.text == "Хорошего дня"

    filter_data = filters.create(filter_text)

    def message_text(client: Client, message: Message):
        """Вывод сообщение, если есть фраза "Хорошего дня"."""
        message.reply('Скоро вернусь с новым материалом!', quote=True)
        client.stop()

    client.add_handler(MessageHandler(message_text, filter_data))

    async def filter_acc(_, __, message):
        """Проверка триггера хорошего дня."""
        return message.text == "/users_today"

    filter_data2 = filters.create(filter_acc)

    def user_check(client: Client, message: Message):
        """Кол-во зарегистрированных людей в БД за сегодня с помощью отправки команды /users_today."""
        if check_admin == True:
            count_user = asyncio.run(view_user())
            message.reply(count_user, quote=True)
        else:
            message.reply('Опция не доступна', quote=True)

    client.add_handler(MessageHandler(user_check, filter_data2))
client.run()
