from pprint import pformat
import requests
import telebot
import os
import traceback


def send_error(excep: Exception, data, where_problem: str) -> None:
    """
    Отправка сообщения с ошибкой
    :param excep:
    :param data:
    :param where_problem:
    """
    msg = f"<b><i>{where_problem}</i></b> @mrdevil73\n\n" \
          f"🟢<b><u>Type Exception:</u></b> {excep.__class__.__name__}\n" \
          f"📄<b><u>Message:</u></b> {excep}\n" \
          f"🧷<b><u>Traceback:</u></b>\n" \
          f"<pre>{traceback.format_exc().replace('<', '-').replace('>', '-')}</pre>\n\n"
    if data:
        msg += f"📂<b><u>Data</u></b>:\n" \
               f"<code>{pformat(data).replace('<', '-').replace('>', '-')}</code>"
    APP_NAME = __package__.split('.')[0].upper()
    requests.post(f"""https://api.telegram.org/bot{os.getenv(f"{APP_NAME}_TOKEN_TG")}/sendMessage?chat_id={os.getenv("MY_TELEGRAM_ID")}&parse_mode=HTML&text={str(msg)}""")


APP_NAME = __package__.split('.')[0].upper()


class MyExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception: Exception):
        """
        :param exception:
        """
        send_error(exception, bot.last_update_id, f"{APP_NAME} Telegram")


bot = telebot.TeleBot(os.getenv(f"{APP_NAME}_TOKEN_TG"), exception_handler=MyExceptionHandler())


def send_message(chat, message, reply_markup=None, parse=None):
    """Send message to telegram"""
    try:
        bot.send_message(chat_id=chat, text=message, reply_markup=reply_markup, parse_mode=parse if parse else None, disable_web_page_preview=True)
    except Exception as ex:
        pass


def edit_message(chat, message_id, message, reply_markup=None):
    """Edit message to telegram"""
    try:
        bot.edit_message_text(chat_id=chat, message_id=message_id, text=message, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as ex:
        print(ex)


def delete_message(chat, message_id):
    """Delete message from telegram"""
    bot.delete_message(chat_id=chat, message_id=message_id)


def inline_message(_id, elements):
    """Answer for inline mode"""
    bot.answer_inline_query(_id, elements, cache_time=0)
