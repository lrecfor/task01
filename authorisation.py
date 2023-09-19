import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils import executor

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils import executor

from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


class RegistrationStates:
    EMAIL = "state:email"
    NAME = "state:name"
    SURNAME = "state:surname"
    PASSWORD = "state:password"


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    # Создаем кнопки для регистрации и авторизации
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    registration_button = types.KeyboardButton("Регистрация")
    login_button = types.KeyboardButton("Авторизация")
    keyboard.add(registration_button, login_button)

    # Отправляем сообщение с кнопками
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text and message.text == "Регистрация")
async def process_registration(message: types.Message):
    await message.answer("Для регистрации, пожалуйста, отправьте свою почту:")

    await RegistrationStates.EMAIL.set()


@dp.message_handler(state=RegistrationStates.EMAIL)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await message.reply(f"Отлично! Теперь отправьте свое имя:")

    await RegistrationStates.NAME.set()


@dp.message_handler(state=RegistrationStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.reply(f"Теперь отправьте свою фамилию:")

    await RegistrationStates.SURNAME.set()


@dp.message_handler(state=RegistrationStates.SURNAME)
async def process_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text

    await message.reply(f"Отправьте свой пароль:")

    await RegistrationStates.PASSWORD.set()


@dp.message_handler(lambda message: message.text, state=RegistrationStates.PASSWORD)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

        # Здесь можно выполнить дополнительные действия, связанные с паролем
        # Например, сохранить данные в базе данных

        await message.reply(f"Спасибо за регистрацию, {data['name']} {data['surname']}!")

        # Возвращаем пользователя в начальное состояние
        await state.finish()
        await process_start(message)


@dp.message_handler(lambda message: message.text and message.text == "Авторизация")
async def process_login(message: types.Message):
    # Добавьте код для обработки авторизации
    await message.answer("Вы выбрали авторизацию. Введите вашу почту и пароль:")


async def process_start(message: types.Message):
    # Вернуть пользователя в начальное состояние
    # Создаем кнопки для регистрации и авторизации
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    registration_button = types.KeyboardButton("Регистрация")
    login_button = types.KeyboardButton("Авторизация")
    keyboard.add(registration_button, login_button)

    # Отправляем сообщение с кнопками
    await message.answer("Выберите действие:", reply_markup=keyboard)


if __name__ == '__main__':
    from aiogram import executor
    from config import TOKEN

    executor.start_polling(dp, skip_updates=True)
