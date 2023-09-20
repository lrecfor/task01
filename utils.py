from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterState(StatesGroup):
    login = State()
    e_mail = State()
    name = State()
    last_name = State()
    create_acc = State()


class SigninState(StatesGroup):
    sign_in = State()
