import re
from .types import MESSAGE_NEW, CALLBACK_UPDATE, Update
import requests
import os
import traceback

# Словари для регистрации обработчиков
message_handlers = {}
callback_handlers = {}


def vkregister_message_handler(func, condition=None, regex=None):
    """
    Новый обработчик сообщений
    """
    if regex:
        message_handlers[lambda updat: re.match(regex, updat.object.message.text.lower())] = func
    elif condition:
        message_handlers[condition] = func


def vkregister_callbackquery_handler(func, condition=None, regex_data=None):
    """
    Новый хендлер callback
    """
    if regex_data:
        callback_handlers[lambda updat: re.match(regex_data, updat.event.payload)] = func
    elif condition:
        callback_handlers[condition] = func


# Функция для обработки запроса
async def process_request(data: Update):
    """
    Поиск нужного обработчика
    :param data: Запрос
    """

    if data.type == MESSAGE_NEW:
        for condition, handler in message_handlers.items():
            if condition(data):
                await handler(data)
                break
    elif data.type == CALLBACK_UPDATE:
        for condition, handler in callback_handlers.items():
            if condition(data):
                await handler(data)
                break
