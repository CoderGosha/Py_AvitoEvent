from helpers.message_helper import MessageHelper
from helpers.storage_helper import StorageHelper
from parsers.avito_parser import AvitoParsing
from services.avito_block_service import AvitoBlockService


class AvitoService:
    def __init__(self, message_helper:MessageHelper):
        self.storage_helper = StorageHelper()
        self.message_helper = message_helper
        self.block_service = AvitoBlockService()

    def do(self):
        # Получим активные парсеры
        active_parsers = self.storage_helper.get_active_parser()
        if not active_parsers:
            return

        # Создадим парсеры и пройдемся по новым данным
        for parser in active_parsers:
            avito_parser = AvitoParsing(parser.url, parser.id, block_service=self.block_service)
            result = avito_parser.parsing_start()
            self.storage_helper.add_products(result)

    def send(self):
        """
            Выбираем новые сообщения и отправляем в шлюз
        :return:
        """
        new_message = self.storage_helper.read_product()
        if not new_message:
            return

        active_link = self.storage_helper.get_active_parser()

        for message in new_message:
            parsers = [i for i in active_link if (message.parser_id == i.id)]
            for parser in parsers:
                for user in parser.users:
                    if user.status and not user.user_block:
                        self.message_helper.bot.send_message(chat_id=user.telegram_id, text=message.to_telegram_str())






