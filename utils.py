from aiogram.dispatcher.filters.state import StatesGroup, State


# classes for FSM
class RegisterState(StatesGroup):
    login = State()
    e_mail = State()
    first_name = State()
    last_name = State()
    create_acc = State()


class SigninState(StatesGroup):
    sign_in = State()
