from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Reg(Base):
    __tablename__ = "reg_info"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(String(), nullable=False)
    password = Column(String(), nullable=False)
    registration_time = Column(DateTime)


class Auth(Base):
    __tablename__ = "auth_info"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey("reg_info.id"), primary_key=True)
    authorization_time = Column(DateTime)
