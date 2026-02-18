'''423361340'''
import logging
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import exceptions
import json
from functions import create_parcel_image
from aiogram.utils.exceptions import (
    MessageToDeleteNotFound,
    MessageCantBeDeleted,
    ChatNotFound,
    UserDeactivated,
    BotBlocked
)


# bot.py


bot = Bot(token='6370693434:AAE9Vj_kV9ztLqmUsxa0k2Wd2G0PUuA4Rdw')
dp = Dispatcher(bot)

try:
    with open('bot_users.json', 'r') as file:
        user_id = json.load(file)
except FileNotFoundError:
    user_id = []

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    # Обработчик команды /start
    # Сохраняем chat ID и user ID пользователя
    if message.from_user.id not in user_id:
        user_id.append(message.from_user.id)
    else:
        await bot.send_message(chat_id=message.from_user.id, text='თქვენ უკვე ხართ ჩატში')




async def send_location_message(trecing, location, info, date):
    # --- Клавиатура ---
    keyboard = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton(
        text="წაშლა",
        callback_data=f"delete_{trecing}"
    )
    keyboard.add(delete_button)

    # --- Создаём изображение и сразу отправляем ---
    image = create_parcel_image(trecing, location, info, date)  # возвращает BytesIO

    # Используем контекстный менеджер, чтобы автоматически закрыть BytesIO
    with image as img_bytes:
        # Если нужно отправить нескольким пользователям, создаём отдельный объект для каждого
        img_data = img_bytes.read()  # читаем данные один раз
        for user in user_id:
            try:
                await bot.send_photo(
                    chat_id=user,
                    photo=BytesIO(img_data),  # создаём новый BytesIO для каждого
                    caption=f"📦{trecing}",
                    reply_markup=keyboard
                )
            except exceptions.BotBlocked:
                continue
            except Exception as e:
                logging.error(f"Ошибка: {e}")
                continue

@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def delete_message(callback_query: types.CallbackQuery):
    try:
        # Получаем tracking (если нужно для логики)
        tracking = callback_query.data.split('_', 1)[1]

        # Удаляем сообщение ТОЛЬКО в текущем чате
        await callback_query.message.delete()

        # Отвечаем на callback (обязательно!)
        await callback_query.answer("Удалено ✅")

        print(f"Сообщение по трекингу {tracking} удалено пользователем {callback_query.from_user.id}")

    except MessageToDeleteNotFound:
        print("Сообщение уже удалено.")

    except MessageCantBeDeleted:
        print("Невозможно удалить сообщение (возможно прошло >48 часов).")

    except UserDeactivated:
        print(f"Пользователь {callback_query.from_user.id} деактивирован.")

    except BotBlocked:
        print(f"Пользователь {callback_query.from_user.id} заблокировал бота.")

    except ChatNotFound:
        print("Чат не найден.")

    except Exception as e:
        print(f"Необработанная ошибка при удалении: {e}")



# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)