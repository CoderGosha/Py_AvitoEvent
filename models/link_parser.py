from sqlalchemy.orm import relationship

from models.user_links import user_link_table
from . import DeclarativeBase
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float


class LinkParser(DeclarativeBase):
    __tablename__ = 'link_parser'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    url = Column(String)

    users = relationship("User",
                         secondary=user_link_table,
                         back_populates="parsers")

    def to_telegram_str(self) -> str:
        return ""

    def to_telegram_bind(self, telegram_id) -> str:
        is_use = [i for i in self.users if telegram_id == str(i.telegram_id)]
        if is_use:
            return "/unbindparser_%i  \n \n  %s" % (self.id, self.url)
        else:
            return "/bindparser_%i  \n \n  %s" % (self.id, self.url)

    def to_telegram_delete(self) -> str:
        return "/delparser_%i  \n User Bind: %i \n  %s" % (self.id, len(self.users), self.url)
