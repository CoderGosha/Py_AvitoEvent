import datetime
import logging
import os
import shutil
import threading
import time

from configuration import Configuration
from helpers.message_helper import MessageHelper
from services.avito_service import AvitoService


class AvitoWorker:
    def __init__(self):
        self.error_count = 0
        self.error_old_time = datetime.datetime.utcnow()
        self.message_helper = MessageHelper()
        self.avito_service = AvitoService(self.message_helper)

        self.th_check_avito = threading.Thread(target=self.do_check_avito)
        self.th_check_avito.daemon = True

        self.th_send_message = threading.Thread(target=self.do_send_message)
        self.th_send_message.daemon = True

        self.th_check_send_message = threading.Thread(target=self.do_check_send_message)
        self.th_check_send_message.daemon = True

        configuration = Configuration()
        self.hour_begin = configuration.config['HOUR_BEGIN']
        self.hour_end = configuration.config['HOUR_END']
        self.timeout_avito = configuration.config['TIMEOUT_MINUTES']

    def start(self):
        self.message_helper.send_notify("Start Avito Bot")
        self.th_check_avito.start()
        self.th_send_message.start()
        self.th_check_send_message.start()

    def do_check_avito(self):
        logging.info("Starting do_check_avito...")
        while True:
            try:
                current_time = datetime.datetime.utcnow()
                if (current_time.hour >= self.hour_begin) and (current_time.hour < self.hour_end):
                    self.avito_service.do()
            except Exception as ex:
                self.increment_error()
                self.message_helper.send_notify("Error check_client:\n" + str(ex))
            finally:
                time.sleep(self.timeout_avito * 60)

    def do_check_send_message(self):
        """
            Проверяем новые сообщения и рассылаем (добавляем в очередь) пользователям по подписке
        :return:
        """
        logging.info("Starting do_check_send_message...")
        try:
            while True:
                self.avito_service.send()
                time.sleep(1)
        except Exception as ex:
            self.increment_error()
            self.message_helper.send_notify("Error check_client:\n" + str(ex))

    def do_send_message(self):
        logging.info("Starting do_message_send...")
        try:
            while True:
                self.message_helper.check_queue()
                time.sleep(1)
        except Exception as ex:
            self.increment_error()
            self.message_helper.send_notify("Error do_message_send:\n" + str(ex))

    def increment_error(self):
        # Если время прошлой ошибки более часа то сбросим счетчик
        if (self.error_old_time + datetime.timedelta(hours=1)) < datetime.datetime.utcnow():
            self.error_count = 0

        self.error_count += 1
        self.error_old_time = datetime.datetime.utcnow()

        if self.error_count > 5:
            self.message_helper.send_notify("App terminated, error count:" + str(self.error_count))
            os._exit(1)
