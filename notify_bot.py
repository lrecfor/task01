from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import N_TOKEN, DATABASE_URL
from database import Database, Reg, Auth
from sqlalchemy import create_engine
from sqlalchemy import Integer, cast
from sqlalchemy.orm import sessionmaker

storage = MemoryStorage()
bot = Bot(token=N_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

db = Database()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Start working")
    url = DATABASE_URL
    engine = create_engine(url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    reg_count = session.query(Reg).count()
    auth_count = session.query(Auth).count()

    while True:
        if session.query(Reg).count() != reg_count:
            reg_count = session.query(Reg).count()
            data = session.query(Reg).order_by(Reg.id.desc()).first()
            await message.answer('New user registered: \n' + 'id: ' + str(data.id) + '\nusername: ' + data.username
                                 + '\nregistration_time: ' + data.registration_time)

        if session.query(Auth).count() != auth_count:
            auth_count = session.query(Auth).count()
            data = session.query(Auth).order_by(Auth.id.desc()).first()
            username = session.query(Reg).join(Auth, cast(Auth.user_id, Integer) == Reg.id).filter(
                data.user_id == cast(Reg.id, Integer)).first().username
            await message.answer('New user authenticated: \n' + 'user_id: ' + data.user_id + '\nusername: ' + username
                                 + '\nauthorization_time: ' + data.authorization_time)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
