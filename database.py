from sqlalchemy import select, cast, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
import config
import models
from asyncpg import Connection
from uuid import uuid4


Base = declarative_base()


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


engine = create_async_engine(config.DATABASE_URL, echo=False, future=True, pool_size=50, connect_args={
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "connection_class": CConnection,
})


Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def SessionManager() -> Session:
    async with Session() as db:
        try:
            yield db
        except:
            await db.rollback()
            raise
        finally:
            await db.close()


async def add(data):
    # function for adding [data] to database
    try:
        async with SessionManager() as session:
            session.add(data)
            await session.commit()
    except Exception as e:
        raise


async def get(data):
    # function for getting data from database by [data]
    try:
        async with SessionManager() as session:
            stmt = select(models.Reg).filter(cast(models.Reg.username, String) == data)
            result = (await session.execute(stmt)).scalars().first()
            await session.close()
        return result
    except Exception as e:
        raise
