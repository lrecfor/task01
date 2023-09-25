from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from database import Database, Reg, Auth
from sqlalchemy import create_engine
from sqlalchemy import Integer, cast
from sqlalchemy.orm import sessionmaker
import logging
import os

storage = MemoryStorage()
bot = Bot(token=config.N_TOKEN)
dp = Dispatcher(bot, storage=storage)
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=config.LOGPATH + config.N_LOGNAME,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='a',
                    level=logging.ERROR)
dp.middleware.setup(LoggingMiddleware())

db = Database()


@dp.message_handler(commands=['start'])  # start command handling
async def start(message: types.Message):
    await message.answer("Start working")
    # connect to database
    url = config.DATABASE_URL
    engine = create_engine(url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # count of rows for each table
    reg_count = session.query(Reg).count()
    auth_count = session.query(Auth).count()

    while True:
        # check if new user registered or authenticated
        if session.query(Reg).count() != reg_count:
            reg_count = session.query(Reg).count()
            data = session.query(Reg).order_by(Reg.id.desc()).first()  # get last row
            await message.answer('New user registered: \n' + 'id: ' + str(data.id) + '\nusername: ' + data.username
                                 + '\nregistration_time: ' + data.registration_time)

        if session.query(Auth).count() != auth_count:
            auth_count = session.query(Auth).count()
            data = session.query(Auth).order_by(Auth.id.desc()).first()  # get last row
            username = session.query(Reg).join(Auth, cast(Auth.user_id, Integer) == Reg.id).filter(
                data.user_id == cast(Reg.id, Integer)).first().username  # get last row's username by user_id
            await message.answer('New user authenticated: \n' + 'user_id: ' + data.user_id + '\nusername: ' + username
                                 + '\nauthorization_time: ' + data.authorization_time)


def execute():
    executor.start_polling(dp, skip_updates=True)
