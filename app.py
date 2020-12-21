from loggerinitializer import initialize_logger
from workers.avito_worker import AvitoWorker
from workers.telegram_worker import TelegramWorker


def main():
    worker = AvitoWorker()
    worker.start()

    telegram_updater = TelegramWorker()
    telegram_updater.updater.idle()



if __name__ == '__main__':
    initialize_logger("log")
    main()

