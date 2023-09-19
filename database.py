from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import exists
from config import DATABASE_URL

base = declarative_base()


class Reg(base):
    __tablename__ = "reg_info"
    id = Column(Integer(), primary_key=True)
    username = Column(String(), nullable=False)
    password = Column(String(), nullable=False)
    registration_time = Column(String(), nullable=False)


class Auth(base):
    __tablename__ = "auth_info"
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False)
    authorization_time = Column(String(), nullable=False)


class Database:
    def __init__(self):
        self.url = DATABASE_URL
        self.engine = create_engine(self.url, echo=True)

    def create(self):
        if not database_exists(self.url):
            create_database(self.url)

        metadata = MetaData()
        reg_table = Table('reg_info', metadata,
                          Column('id', Integer(), primary_key=True),
                          Column('username', String(), nullable=False),
                          Column('password', String(), nullable=False),
                          Column('registration_time', String(), nullable=False)
                          )
        auth_table = Table('auth_info', metadata,
                           Column('id', Integer(), primary_key=True),
                           Column('user_id', String(), nullable=False),
                           Column('authorization_time', String(), nullable=False),
                           )
        metadata.create_all(self.engine)

    def add(self, news_list):
        self.create()
        Session = sessionmaker(bind=self.engine)
        session = Session()
        for new in news_list:
            if session.query(exists().where(New.title == new.title)).scalar() is False:
                session.add(new)
        session.commit()
        session.close()

    def get(self, new_id):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(New).filter_by(id=new_id).first()
        session.close()
        return res
