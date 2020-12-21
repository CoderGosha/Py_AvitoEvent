import datetime

from sqlalchemy.orm import relationship

from models.user_links import user_link_table
from . import DeclarativeBase
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float


class User(DeclarativeBase):
    __tablename__ = 'users'
    telegram_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String)
    user_description = Column(String)
    create_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Boolean, default=True)
    user_block = Column(Boolean, default=False)

    parsers = relationship("LinkParser",
                           secondary=user_link_table,
                           back_populates="users")

    def __init__(self, telegram_id, username, user_description):
        self.username = username
        self.telegram_id = telegram_id
        self.user_description = user_description

    def to_telegram_str(self) -> str:
        return "UN: %s \nDescription: %s \nStatus: %s \nIs block: %s\nCreate user: %s" % (
            self.username, self.user_description, self.status, self.user_block, self.create_date)

    def to_telegram_stats(self) -> str:
        return "UN: %s \nDescription: %s\nStatus: %s\nIs block: %s\nCreate user: %s \nCount parser: %i\n /changestatus_%i" \
               % (
                   self.username, self.user_description, self.status, self.user_block, self.create_date,
                   len(self.parsers), self.telegram_id)

    def to_telegram_bind(self) -> str:
        return "UN: %s \nDescription: %s\nStatus: %s\nIs block: %s\nCreate user: %s \nCount parser: %i\n /binduser_%i" \
               % (
                   self.username, self.user_description, self.status, self.user_block, self.create_date,
                   len(self.parsers), self.telegram_id)
