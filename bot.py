from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from config import TOKEN
from utils import RegisterState, SigninState
from database import Database, Reg, Auth
from datetime import datetime
import hashlib

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

db = Database()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    register_btn = types.KeyboardButton("Create an account")
    sign_in_btn = types.KeyboardButton("Sign in")
    buttons.add(sign_in_btn, register_btn)

    await message.answer("Please select an action:", reply_markup=buttons)


# authorisation button handling
@dp.message_handler(lambda message: message.text and message.text == "Sign in")
async def authorisation(message: types.Message):
    await message.answer("For authorisation, please send your login:")
    await SigninState.sign_in.set()


@dp.message_handler(state=SigninState.sign_in)  # func to sign in
async def sign_in(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    data = await state.get_data()
    user_data = db.get(data["login"])
    if user_data is None:
        await message.answer("Account was not found. Please, try again or create an account.")
    else:
        # sign in
        await message.answer("Account was found. You sign in successfully.")
        db.add(Auth(user_id=user_data.id, authorization_time=datetime.now()))
    await state.finish()


# registration button handling
@dp.message_handler(lambda message: message.text and message.text == "Create an account")
async def registration(message: types.Message):
    await message.answer("For registration, please send your login:")
    await RegisterState.login.set()


@dp.message_handler(state=RegisterState.login)  # get login from user
async def get_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Ok, now send your e-mail:")
    await RegisterState.e_mail.set()


@dp.message_handler(state=RegisterState.e_mail)  # get e-mail from user
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(e_mail=message.text)
    await message.answer("Send your name:")
    await RegisterState.name.set()


@dp.message_handler(state=RegisterState.name)  # get name from user
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Your last name:")
    await RegisterState.last_name.set()


@dp.message_handler(state=RegisterState.last_name)  # get last name from user
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("And your password:")
    await RegisterState.create_acc.set()


@dp.message_handler(state=RegisterState.create_acc)  # func to create account
async def create_acc(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    login = db.get(data["login"])
    if login is not None:
        await message.answer("User with this login is already exist. Please, use another login or sign in.")
    else:
        # create account
        password = hashlib.sha512(data['password'].encode()).hexdigest()
        db.add(Reg(username=data['login'], password=password, registration_time=datetime.now()))
        await message.answer(f"Account {data['login']} was created successfully")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
