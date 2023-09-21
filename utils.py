from aiogram.dispatcher.filters.state import StatesGroup, State
from selenium import webdriver
import time


class RegisterState(StatesGroup):
    login = State()
    e_mail = State()
    first_name = State()
    last_name = State()
    create_acc = State()


class SigninState(StatesGroup):
    sign_in = State()


def connect_driver():
    driver = webdriver.Firefox()
    driver.get("http://cappa.csu.ru/")
    driver.find_element("class name", "profile__bar-login").click()
    time.sleep(1)
    return driver
