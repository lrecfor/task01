from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import config
import psycopg2

base = declarative_base()


class Reg(base):
    __tablename__ = "reg_info"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(String(), nullable=False)
    password = Column(String(), nullable=False)
    registration_time = Column(String(), nullable=False)


class Auth(base):
    __tablename__ = "auth_info"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey("reg_info.id"), primary_key=True)
    authorization_time = Column(String(), nullable=False)


class Database:
    def __init__(self):
        self.url = config.DATABASE_URL
        self.engine = create_engine(self.url, echo=True)

        if not database_exists(self.url):
            create_database(self.url)

        metadata = MetaData()
        # table for registration info
        reg_table = Table('reg_info', metadata,
                          Column('id', Integer(), primary_key=True),
                          Column('username', String(), nullable=False),
                          Column('password', String(), nullable=False),
                          Column('registration_time', String(), nullable=False)
                          )

        # table for authentication info
        auth_table = Table('auth_info', metadata,
                           Column('id', Integer(), primary_key=True),
                           Column('user_id', String(), nullable=False),
                           Column('authorization_time', String(), nullable=False),
                           )
        metadata.create_all(self.engine)

    def add(self, data):
        # function for adding [data] to database
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add(data)
        session.commit()
        session.close()

    def get(self, data):
        # function for getting data from database by [data]
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Reg).filter_by(username=data).first()
        if res:
            session.close()
        else:
            res = None
        return res
