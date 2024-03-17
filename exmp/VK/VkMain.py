import json
import os
from .types import Bot
import random

APP_NAME = __package__.split('.')[0].upper()
TOKEN = os.getenv(f"{APP_NAME}_TOKEN_VK")

bot = Bot(token=TOKEN)


async def send_message(peer_id, text, reply_markup=''):
    """

    :param peer_id:
    :param text:
    :param reply_markup:
    """
    await bot.send_message(peer_id=peer_id, message=text, keyboard=reply_markup, random_id=random.randint(444, 444444), dont_parse_links=1)


async def edit_message(peer_id, convers_id, text, reply_markup=None):
    """

    :param peer_id:
    :param convers_id:
    :param text:
    :param reply_markup:
    """
    await bot.edit_message(peer_id=peer_id, conversation_message_id=convers_id, message=text, keyboard=reply_markup, dont_parse_links=1)


async def delete_message(peer_id, convers_id):
    """

    :param peer_id:
    :param convers_id:
    """
    await bot.delete_message(peer_id=peer_id, convers_id=convers_id)


def user_get(user_id):
    """

    :param user_id:
    :return:
    """
    return bot.user_get(user_id)


def send_event(event_id, peer_id, user_id):
    """

    :param event_id:
    :param peer_id:
    :param user_id:
    :return:
    """
    return bot.req("messages.sendMessageEventAnswer", event_id=event_id,
                   peer_id=peer_id, user_id=user_id, event_data=json.dumps({"type": "show_snackbar", "text": "test"}))
