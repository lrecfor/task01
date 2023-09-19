from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from config import TOKEN
from utils import RegisterState, SigninState


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    register_btn = types.KeyboardButton("Create an account")
    sign_in_btn = types.KeyboardButton("Sign in")
    buttons.add(sign_in_btn, register_btn)

    await message.answer("Please select an action:", reply_markup=buttons)


@dp.message_handler(lambda message: message.text and message.text == "Sign in")
async def authorisation(message: types.Message):
    await message.answer("For authorisation, please send your e-mail or login:")
    await SigninState.login.set()


@dp.message_handler(state=SigninState.login)
async def get_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    data = await state.get_data()
    print(data)
    await message.answer("Account was found. You sign in successfully.")

    await state.finish()


@dp.message_handler(lambda message: message.text and message.text == "Create an account")
async def registration(message: types.Message):
    await message.answer("For registration, please send your e-mail:")
    await RegisterState.e_mail.set()


@dp.message_handler(state=RegisterState.e_mail)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(e_mail=message.text)
    await message.answer("Ok, now send your name:")
    await RegisterState.name.set()


@dp.message_handler(state=RegisterState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Your last name:")
    await RegisterState.last_name.set()


@dp.message_handler(state=RegisterState.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("And your password:")
    await RegisterState.password.set()


@dp.message_handler(state=RegisterState.password)
async def get_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(f"Your data:\n"
                         f"E-mail: {data['e_mail']}\n"
                         f"Name: {data['name']}\n"
                         f"Last name: {data['last_name']}\n"
                         f"Password: {data['password']}\n"
                         f"Account was created successfully")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
