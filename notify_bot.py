from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from database import SessionManager
from models import Reg, Auth
from sqlalchemy import Integer, cast, select
import models

storage = MemoryStorage()
bot = Bot(token=config.N_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # function for start command handling
    # get data from database in loop and send message to user when new user registered or authenticated
    await message.answer("Start working")

    try:
        async with SessionManager() as session:
            reg_count = len((await session.execute(select(models.Reg))).all())
            auth_count = len((await session.execute(select(models.Auth))).all())

            while True:
                if len((await session.execute(select(models.Reg))).all()) != reg_count:
                    reg_count = len((await session.execute(select(models.Reg))).all())
                    stmt = select(models.Reg).order_by(Reg.id.desc())
                    data = (await session.execute(stmt)).scalars().first()
                    await message.answer('New user registered: \n' + 'id: ' + str(data.id) + '\nusername: ' + data.username
                                         + '\nregistration_time: ' + data.registration_time)

                if len((await session.execute(select(models.Auth))).all()) != auth_count:
                    auth_count = len((await session.execute(select(models.Auth))).all())
                    stmt = select(models.Auth).order_by(Auth.id.desc())
                    data = (await session.execute(stmt)).scalars().first()
                    stmt = select(models.Reg).join(Auth, cast(Auth.user_id, Integer) == Reg.id).filter(
                        int(data.user_id) == cast(Reg.id, Integer))
                    username = (await session.execute(stmt)).scalars().first().username
                    await message.answer('New user authenticated: \n' + 'user_id: ' + data.user_id + '\nusername: ' + username
                                         + '\nauthorization_time: ' + data.authorization_time)
    except Exception as e:
        await message.answer("Something was wrong. Bot stopped working.")
