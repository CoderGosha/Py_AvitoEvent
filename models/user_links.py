from . import DeclarativeBase
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Table, ForeignKey

user_link_table = Table('user_link_table', DeclarativeBase.metadata,
    Column('user_id', Integer, ForeignKey('users.telegram_id')),
    Column('parser_id', Integer, ForeignKey('link_parser.id'))
)