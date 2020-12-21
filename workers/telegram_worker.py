# -*- coding: utf-8 -*-


import traceback
from functools import partial

import logging

import os
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, Updater, ConversationHandler, Filters, MessageHandler, RegexHandler

from configuration import Configuration
from extensions.telegram_ext import catch_exceptions, on_error, admin_check, user_state_check
from helpers.storage_helper import StorageHelper
from models.user import User

ASKED_NEW_USER, ASKED_DEACTIVATE_USER, ASKED_NEW_LINK, ASKED_BIND_USER, ASKED_PARSER, ASKED_DEL_LINK = list(range(6))


class TelegramWorker:
    def __init__(self):
        configuration = Configuration()
        self.token_bot = configuration.config['TELEGRAM']['BOT_TOKEN']
        self.admins = configuration.config["ADMINS"]
        self.users_state = dict()
        self.storage_helper = StorageHelper()
        self.updater = Updater(self.token_bot, use_context=False)

        dp = self.updater.dispatcher
        dp.add_error_handler(on_error)
        dp.add_handler(CommandHandler('start', self.start))

        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('newuser', self.new_user)],
            states={
                ASKED_NEW_USER: [
                    MessageHandler(Filters.forwarded, self.new_user_add)
                ],
            },
            allow_reentry=True,
            fallbacks=[CommandHandler('cancel', self.start)]
        ))

        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('statusers', self.change_status_user)],
            states={
                ASKED_DEACTIVATE_USER: [
                    MessageHandler(Filters.command, self.change_status_user_do)
                ],
            },
            allow_reentry=True,
            fallbacks=[CommandHandler('cancel', self.start)]
        ))

        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('newlink', self.new_link)],
            states={
                ASKED_NEW_LINK: [
                    MessageHandler(Filters.regex('^https://www.avito.ru/'), self.new_link_add)
                ],
            },
            allow_reentry=True,
            fallbacks=[CommandHandler('cancel', self.start)]
        ))
        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('dellink', self.del_link)],
            states={
                ASKED_DEL_LINK: [
                    MessageHandler(Filters.regex('^/delparser'), self.del_parser)
                ],
            },
            allow_reentry=True,
            fallbacks=[CommandHandler('cancel', self.start)]
        ))
        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('binduser', self.binduser)],
            states={
                ASKED_BIND_USER: [
                    MessageHandler(Filters.command, self.list_parser)
                ],
                ASKED_PARSER: [
                    MessageHandler(Filters.regex('^/bindparser'), self.bind_parser),
                    MessageHandler(Filters.regex('^/unbindparser'), self.unbind_parser)
                ]
            },
            allow_reentry=True,
            fallbacks=[CommandHandler('cancel', self.start)]
        ))

        logging.info('Starting long poll')
        self.updater.start_polling()

    @catch_exceptions
    @admin_check
    def start(self, bot, update):
        text = "%s \n%s \n%s \n%s \n%s \n%s \n%s \n" % ("Команда /newuser добавит пользователя",
                                                       "Команда /statusers покажет пользователей \n",
                                                       "Команда /newlink добавит ссылку",
                                                       "Команда /dellink удалит ссылку",
                                                       "Команда /binduser свяжет пользователя с парсером",
                                                       "",
                                                       "По вопросам пишите @CoderGosha")

        update.message.reply_text(text)
        self.users_state[update.message.from_user.id] = dict()

   # @catch_exceptions
    @admin_check
    def new_user(self, bot, update):
        update.message.reply_text('Хорошо. Перешлите любое сообщение от нового пользователя')
        return ASKED_NEW_USER

    #@catch_exceptions
    @admin_check
    def new_user_add(self, bot, update):
        telegram_id = str(update.message.forward_from.id)
        username = update.message.forward_from.username
        user_description = "%s" % update.message.forward_from.full_name

        user = User(telegram_id=telegram_id, username=username, user_description=user_description)
        self.storage_helper.user_add(user)

        update.message.reply_text('Готово!')
        update.message.reply_text('Добавлен новый пользователь @%s' % username)

        return ConversationHandler.END

    #@catch_exceptions
    @admin_check
    def change_status_user(self, bot, update):
        users = self.storage_helper.get_stat_users()
        for user in users:
            update.message.reply_text(user.to_telegram_stats())
        if not users:
            update.message.reply_text("Нет пользоваетлей")
            return ConversationHandler.END
        return ASKED_DEACTIVATE_USER

    #@catch_exceptions
    @admin_check
    def change_status_user_do(self, bot, update):
        telegram_id = update.message.text.split('/changestatus_')[-1]
        self.storage_helper.user_change_status(telegram_id)
        update.message.reply_text('Готово!')
        return ConversationHandler.END

    #@catch_exceptions
    @admin_check
    def new_link(self, bot, update):
        update.message.reply_text('Хорошо. Пришлите ссылку с авито')
        return ASKED_NEW_LINK

    #@catch_exceptions
    @admin_check
    def del_link(self, bot, update):
        parsers = self.storage_helper.get_link_parser()
        for parser in parsers:
            update.message.reply_text(parser.to_telegram_delete())
        if not parsers:
            update.message.reply_text("Нет парсеров")
            return ConversationHandler.END

        return ASKED_DEL_LINK

    #@catch_exceptions
    @admin_check
    def del_parser(self, bot, update):
        parser_id = update.message.text.split('/delparser_')[-1]
        self.storage_helper.link_del(parser_id)
        update.message.reply_text('Готово!')
        update.message.reply_text('Ссылка удалена %s' % parser_id)
        return ConversationHandler.END

    #@catch_exceptions
    @admin_check
    def new_link_add(self, bot, update):
        url = update.message.text
        self.storage_helper.link_add(url)
        update.message.reply_text('Готово!')
        update.message.reply_text('Ссылка добавлена %s' % url)
        return ConversationHandler.END

    #@catch_exceptions
    @admin_check
    def binduser(self, bot, update):
        users = self.storage_helper.get_stat_users()
        for user in users:
            update.message.reply_text(user.to_telegram_bind())
        if not users:
            update.message.reply_text("Нет пользоваетлей")
            return ConversationHandler.END
        return ASKED_BIND_USER

    #@catch_exceptions
    @admin_check
    @user_state_check
    def list_parser(self, bot, update):
        # Запомнить пользователя
        telegram_id = update.message.text.split('/binduser_')[-1]
        parsers = self.storage_helper.get_link_parser()
        for parser in parsers:
            update.message.reply_text(parser.to_telegram_bind(telegram_id))
        if not parsers:
            update.message.reply_text("Нет парсеров")
            return ConversationHandler.END

        self.users_state[update.message.from_user.id]["current_bind"] = telegram_id
        return ASKED_PARSER

    #@catch_exceptions
    @admin_check
    @user_state_check
    def bind_parser(self, bot, update):
        telegram_id = self.users_state[update.message.from_user.id]["current_bind"]
        parser_id = update.message.text.split('/bindparser_')[-1]
        # self.storage_helper.user_change_status(telegram_id)
        if parser_id:
            self.storage_helper.add_parser_to_user(telegram_id, parser_id)
            self.users_state[update.message.from_user.id]["current_bind"] = None
        update.message.reply_text('Готово!')
        return ConversationHandler.END

    #@catch_exceptions
    @admin_check
    @user_state_check
    def unbind_parser(self, bot, update):
        telegram_id = self.users_state[update.message.from_user.id]["current_bind"]
        parser_id = update.message.text.split('/unbindparser_')[-1]
        if parser_id:
            self.storage_helper.del_parser_to_user(telegram_id, parser_id)
            self.users_state[update.message.from_user.id]["current_bind"] = None
        update.message.reply_text('Готово!')
        return ConversationHandler.END
