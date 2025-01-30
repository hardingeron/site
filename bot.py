'''423361340'''
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import exceptions
import json


# bot.py


bot = Bot(token='6370693434:AAEEPDaX9BrzkY07Xsp78AlP8Z4owmXSVX0')
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
    message_text = f"------------------------------------------------------------\nთრექინგი  --  {trecing}\n\nთარო  --  {location}\n\nნომერი  --  {info}\n\nთარიღი  --  {date}\n------------------------------------------------------------"
    keyboard = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton(text="წაშლა", callback_data=f"delete_{trecing}")
    keyboard.add(delete_button)
    
    for user in user_id:
        try:
            await bot.send_message(chat_id=user, text=message_text, reply_markup=keyboard)
        except exceptions.BotBlocked as e:
            logging.error(f"Пользователь {user} заблокировал бота")
            continue  # Пропустить итерацию и перейти к следующему пользователю
        except Exception as e:
            logging.error(f"Необработанная ошибка при отправке сообщения пользователю {user}: {e}")
            continue  # Пропустить итерацию и перейти к следующему пользователю

@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def delete_message(callback_query: types.CallbackQuery):
    trecing = callback_query.data.split('_')[1]
    message_id = callback_query.message.message_id
    for user in user_id:
        try:
            await bot.delete_message(chat_id=user, message_id=message_id)
        except Exception as e:
            print(f"Failed to delete message for user {user}: {e}")

    await bot.answer_callback_query(callback_query.id)  # Отправка ответа на callback-запрос




# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)