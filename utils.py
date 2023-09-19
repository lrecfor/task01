from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterState(StatesGroup):
    e_mail = State()
    name = State()
    last_name = State()
    password = State()


class SigninState(StatesGroup):
    login = State()
