import logging
import traceback

from configuration import Configuration

configuration = Configuration()
admins = configuration.config["ADMINS"]


def catch_exceptions(func):
    def wrapper(worker, bot, update, *args, **kwargs):
        try:
            return func(worker, bot, update, *args, **kwargs)
        except Exception as e:
            on_error_legacy(worker, bot, update, e)

    return wrapper


def on_error(bot, update, error):
    logging.error('Update "{}" caused error "{}"'.format(update, error))
    traceback.print_exc()

    if update is not None:
        update.message.reply_text('Внутренняя ошибка')
        update.message.reply_text('{}: {}'.format(type(error).__name__, str(error)))
        update.message.reply_text('Сообщите @CoderGosha')


def on_error_legacy(worker, bot, update, error):
    logging.error('Update "{}" caused error "{}"'.format(update, error))
    traceback.print_exc()

    if update is not None:
        update.message.reply_text('Внутренняя ошибка')
        update.message.reply_text('{}: {}'.format(type(error).__name__, str(error)))
        update.message.reply_text('Сообщите @CoderGosha')


def admin_check(func):
    def wrapper(worker, bot, update, *args, **kwargs):
        if update.message.from_user.id in admins:
            return func(worker, bot, update, *args, **kwargs)
        else:
            update.message.reply_text('Доступ ограничен. Вы не являетесь администратором')
            update.message.reply_text('По вопросам пишите @CoderGosha')
    return wrapper


def user_state_check(func):
    def wrapper(worker, bot, update, *args, **kwargs):
        if update.message.from_user.id not in worker.users_state:
            worker.users_state[update.message.from_user.id] = dict()
        return func(worker, bot, update, *args, **kwargs)
    return wrapper

