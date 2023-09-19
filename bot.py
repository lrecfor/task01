from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton


API_TOKEN = '6536807460:AAG_D_j8DjFSaCK6GWGGIp_ceHXomT4THz0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

BUTTON_1 = 0
BUTTON_2 = 0


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    button1 = InlineKeyboardButton("Sign in")
    button2 = InlineKeyboardButton("Create an account")

    buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1, button2)
    await message.reply("Please select:", reply_markup=buttons)


@dp.message_handler()
async def answer(message: types.Message):  # анализируем ответ пользователя
    global BUTTON_1
    global BUTTON_2

    if BUTTON_1 == 1:  # нажата первая кнопка
        BUTTON_1 = 0
        await message.answer("Button1")

    elif BUTTON_2 == 1:  # нажата вторая кнопка
        BUTTON_2 = 0
        await message.answer("Button2")


@dp.callback_query_handler(text='Sign in')
async def process_callback_button1(callback_query: types.CallbackQuery):  # обработка нажатия второй кнопки
    global BUTTON_2
    BUTTON_2 = 1  # отмечаем, что была нажата первая кнопка
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Sign in')


@dp.callback_query_handler(text='Create an account')
async def process_callback_button2(callback_query: types.CallbackQuery):  # обработка нажатия второй кнопки
    global BUTTON_2
    BUTTON_2 = 1  # отмечаем, что была нажата первая кнопка
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Create')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
