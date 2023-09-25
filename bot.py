from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from selenium.common import NoSuchElementException
from utils import RegisterState, SigninState, connect_driver
from database import Database, Reg, Auth
from datetime import datetime
from cryptography.fernet import Fernet
import time
import logging
import config
import os

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
    user_data = db.get(data["username"])
    username = user_data.username
    password = fernet.decrypt(user_data.password).decode('utf-8')
    driver = connect_driver()

    # field filling
    driver.find_element("xpath", '//*[@id="id_login"]').send_keys(username)
    driver.find_element("xpath", '//*[@id="id_password"]').send_keys(password)
    # submit button clicking
    driver.find_element("xpath", '/html/body/div[1]/main/div/div[2]/div/form/input[5]').click()

    # error checking
    try:
        if (driver.find_element("xpath", '/html/body/div/main/div/div[2]/div/form/small').text ==
                "Проверьте правильность написания логина и пароля"):
            driver.close()
            await message.answer("Account was not found. Check your login and try again or create an account.")
    except NoSuchElementException:  # no errors
        driver.close()
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

    # account creation
    driver = connect_driver()
    # registration button search
    driver.find_element("xpath", "/html/body/div[1]/main/div/div[2]/div/form/a").click()
    time.sleep(1)
    # field search and input data
    input_fields = driver.find_elements("class name", 'form-control')
    for field in input_fields:
        field_value = data.get(field.get_attribute('name'))
        field.send_keys(field_value)
    # submit button search
    driver.find_element("xpath", '/html/body/div/main/div/div[2]/div/form/input[3]').click()

    # error checking
    try:
        error_text = ""
        if (driver.find_element("xpath", "/html/body/div/main/div/div[2]/div/form/small/ul[1]/li").text ==
                "Пользователь с таким логином уже существует"):
            error_text = f"Account {data['username']} already exists. Please, use another login or sign in."
        elif (driver.find_element("xpath", "/html/body/div/main/div/div[2]/div/form/small/ul[1]/li").text ==
              "Пользователь с такой почтой уже существует"):
            error_text = f"Account with e-mail {data['email']} already exists. Please, use another e-mail or sign in."
        elif (driver.find_element("xpath", "/html/body/div/main/div/div[2]/div/form/small/ul[1]/li").text ==
              "Введите правильный адрес электронной почты"):
            error_text = f"Incorrect e-mail {data['email']}"
        elif (driver.find_element("xpath", "/html/body/div/main/div/div[2]/div/form/small/ul[1]/li").text ==
              "Пароль должен быть больше 5 символов"):
            error_text = f"Password should be more than 5 characters"

        driver.close()
        await message.answer(error_text)
    except NoSuchElementException:  # account was created without errors
        driver.close()
        password = fernet.encrypt(data["password1"].encode('utf-8')).decode('utf-8')
        db.add(Reg(username=data['username'], password=password, registration_time=datetime.now()))
        await message.answer(f"Account {data['username']} was created successfully")

    await state.finish()


def execute():
    executor.start_polling(dp, skip_updates=True)
