import copy
from typing import List

from sqlalchemy.orm import lazyload, joinedload

from models.link_parser import LinkParser
from models.product import Product
from models.user import User
from services.storage_service import StorageService


class StorageHelper:
    def __init__(self):
        self.storage_service = StorageService()

    def user_add(self, user: User):
        session = self.storage_service.create_session()
        db_item = session.query(User).filter_by(telegram_id=user.telegram_id).first()
        if not db_item:
            # Добавить в хранилище
            session.add(user)
        session.commit()
        session.close()

    def get_active_users(self)->List[User]:
        session = self.storage_service.create_session()
        db_items = session.query(User).filter_by(status=True).all()
        session.expunge_all()
        session.close()
        return db_items

    def get_stat_users(self)->List[User]:
        session = self.storage_service.create_session()
        db_items = session.query(User).options(joinedload(User.parsers)).all()
        session.expunge_all()
        session.close()
        return db_items

    def user_change_status(self, telegram_id):
        session = self.storage_service.create_session()
        db_item = session.query(User).filter_by(telegram_id=telegram_id).first()
        if db_item:
            # Добавить в хранилище
            db_item.status = not db_item.status
        session.commit()
        session.close()

    def link_add(self, url):
        session = self.storage_service.create_session()
        db_item = session.query(LinkParser).filter_by(url=url).first()
        if not db_item:
            # Добавить в хранилище
            session.add(LinkParser(url=url))
        session.commit()
        session.close()

    def get_link_parser(self)->List[LinkParser]:
        session = self.storage_service.create_session()
        db_items = session.query(LinkParser).options(joinedload(LinkParser.users)).all()
        session.expunge_all()
        session.close()
        return db_items

    def add_parser_to_user(self, telegram_id, parser_id):
        session = self.storage_service.create_session()
        db_user = session.query(User).get(telegram_id)
        db_parser = session.query(LinkParser).get(parser_id)
        if db_user:
            # Добавить в хранилище
            db_user.parsers.append(db_parser)
        session.commit()
        session.close()

    def del_parser_to_user(self, telegram_id, parser_id):
        session = self.storage_service.create_session()
        db_user = session.query(User).get(telegram_id)
        db_parser = session.query(LinkParser).get(parser_id)
        if db_user:
            # Добавить в хранилище
            db_user.parsers.remove(db_parser)
        session.commit()
        session.close()

    def get_active_parser(self):
        session = self.storage_service.create_session()
        db_items = session.query(LinkParser).options(joinedload(LinkParser.users)).all()
        active_parser = []
        for parser in db_items:
            active_users = [i for i in parser.users if (i.status and not i.user_block)]
            if active_users:
                active_parser.append(parser)
        session.expunge_all()
        session.close()
        return active_parser

    def add_products(self, products: List[Product]):
        if not products:
            return
        session = self.storage_service.create_session()
        for product in products:
            db_item = session.query(Product).filter_by(url=product.url).first()
            if not db_item:
                session.add(product)
        session.commit()
        session.close()

    def read_product(self) -> List[Product]:
        session = self.storage_service.create_session()
        unread_transaction = session.query(Product).filter_by(is_send=0).all()
        for item in unread_transaction:
            session.query(Product).filter_by(url=item.url). \
                update({"is_send": 1})
        read_product = copy.deepcopy(unread_transaction)
        session.commit()
        session.close()
        return read_product

    def link_del(self, parser_id):
        session = self.storage_service.create_session()
        db_item = session.query(LinkParser).get(parser_id)
        if db_item:
            # удалим в хранилище
            session.delete(db_item)
        session.commit()
        session.close()


