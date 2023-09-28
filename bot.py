from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from selenium.common import NoSuchElementException
from utils import RegisterState, SigninState
from database import Database, Reg, Auth
from datetime import datetime
from cryptography.fernet import Fernet
import time
import logging
import config
import os
import asyncio
from driver import Driver

fernet = Fernet(config.KEY)

storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=config.LOGPATH + config.LOGNAME,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='a',
                    level=logging.ERROR)
dp.middleware.setup(LoggingMiddleware())

db = Database()


# start command handling, button output
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


# func to sign in
@dp.message_handler(state=SigninState.sign_in)  # func to sign in
async def sign_in(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    try:
        user_data = db.get(data["username"])
        username = user_data.username
        password = fernet.decrypt(user_data.password).decode('utf-8')
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.answer("Error.")
        await state.finish()
    driver = Driver()

    # field filling
    # driver.find_element("xpath", '//*[@id="id_login"]').send_keys(username)
    # driver.find_element("xpath", '//*[@id="id_password"]').send_keys(password)
    # # submit button clicking
    # driver.find_element("xpath", '/html/body/div[1]/main/div/div[2]/div/form/input[5]').click()
    try:
        await driver.open_browser_for_sign_in()
        await driver.fill_element('#id_login', username)
        await driver.fill_elements('#id_password', password)
        await driver.click_element('.btn')
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    # error checking
    try:
        if (await driver.find_element('.msg') ==
                "Проверьте правильность написания логина и пароля"):
            await message.answer("Account was not found. Check your login and try again or create an account.")
    except NoSuchElementException:  # no errors
        db.add(Auth(user_id=user_data.id, authorization_time=datetime.now()))
        await message.answer("You signed in successfully.")
    await state.finish()


# registration button handling
@dp.message_handler(lambda message: message.text and message.text == "Create an account")
async def registration(message: types.Message):
    await message.answer("For registration, please send your login:")
    await RegisterState.login.set()


# get login from user
@dp.message_handler(state=RegisterState.login)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Ok, now send your e-mail:")
    await RegisterState.e_mail.set()


# get e-mail from user
@dp.message_handler(state=RegisterState.e_mail)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Send your name:")
    await RegisterState.first_name.set()


# get name from user
@dp.message_handler(state=RegisterState.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Your last name:")
    await RegisterState.last_name.set()


# get last name from user
@dp.message_handler(state=RegisterState.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("And your password:")
    await RegisterState.create_acc.set()


# func to create account
@dp.message_handler(state=RegisterState.create_acc)
async def create_acc(message: types.Message, state: FSMContext):
    await state.update_data(password1=message.text)
    await state.update_data(password2=message.text)
    data = await state.get_data()

    driver = Driver()
    try:
        await driver.open_browser_for_cr(data)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    # error checking
    try:
        error_text = ""
        if (await driver.find_element('.msg') ==
                "Пользователь с таким логином уже существует"):
            error_text = f"Account {data['username']} already exists. Please, use another login or sign in."
        elif (await driver.find_element('.msg') ==
              "Пользователь с такой почтой уже существует"):
            error_text = f"Account with e-mail {data['email']} already exists. Please, use another e-mail or sign in."
        elif (await driver.find_element('.msg') ==
              "Введите правильный адрес электронной почты"):
            error_text = f"Incorrect e-mail {data['email']}"
        elif (await driver.find_element('.msg') ==
              "Пароль должен быть больше 5 символов"):
            error_text = f"Password should be more than 5 characters"

        await message.answer(error_text)
    except NoSuchElementException:  # account was created without errors
        password = fernet.encrypt(data["password1"].encode('utf-8')).decode('utf-8')
        db.add(Reg(username=data['username'], password=password, registration_time=datetime.now()))
        await message.answer(f"Account {data['username']} was created successfully")

    await state.finish()


def execute():
    executor.start_polling(dp, skip_updates=True)


execute()
