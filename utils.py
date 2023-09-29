from aiogram.dispatcher.filters.state import StatesGroup, State
import logging
import config
import os


# classes for FSM
class RegisterState(StatesGroup):
    login = State()
    e_mail = State()
    first_name = State()
    last_name = State()
    create_acc = State()


class SigninState(StatesGroup):
    sign_in = State()


def set_logger():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(filename=config.LOGPATH + config.LOGNAME,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S',
                        filemode='a',
                        level=logging.DEBUG)
