# -*- coding: utf-8 -*-
import json
import time
import os

from django.http import HttpResponse
from django.shortcuts import render

from telebot import types
from .Telegram.set_handlers import bot
from django.views.decorators.csrf import csrf_exempt

from .VK import types as Vktypes
from .VK.set_handlers import process_request
from .Telegram.TgMain import send_error

from .logg import LoggEvent

APP_NAME = __package__.split('.')[0].upper()
TOKEN_TG = os.getenv(f"{APP_NAME}_SECRET_TOKEN_TG")
TOKEN_VK = os.getenv(f"{APP_NAME}_SECRET_TOKEN_VK")
CONFIRM_CODE_VK = os.getenv(f"{APP_NAME}_VK_RESPONSE")

@csrf_exempt
def TgParse(request):
    """
    :param request:
    :return:
    """
    data = ""
    try:
        token_telegram = request.headers.get("X-Telegram-Bot-Api-Secret-Token", None)
        if token_telegram != TOKEN_TG:
            return HttpResponse("F u", status=418)
        data = request.body.decode('UTF-8', 'ignore')
        update = types.Update.de_json(data)
        bot.process_new_updates([update])
    except json.JSONDecodeError:
        pass
    except Exception as ex:
        LoggEvent("SYS", 444, "ErrorViewTG", (str(ex) + "   " + str(data)).replace('\n', ';;;'))
        send_error(ex, data, "УлГУ ТГ")

    return HttpResponse("Ok", status=200)


async def VkParse(request):
    """
    Parsing VK
    :param request:
    :return:
    """
    data = ""
    try:
        data = json.loads(request.body.decode('UTF-8', 'ignore'))
        if data.get("secret", None) != TOKEN_VK:
            return HttpResponse("F u", status=418)

        if data.get("type", None) == "confirmation":
            return HttpResponse(CONFIRM_CODE_VK, status=200)

        tes = Vktypes.Update(data)
        await process_request(tes)
    except json.JSONDecodeError:
        pass
    except Exception as ex:
        LoggEvent("SYS", 444, "ErrorViewVK", (str(ex) + "   " + str(data)).replace('\n', ';;;'))
        send_error(ex, data, "УлГУ ВК")

    return HttpResponse('Ok', status=200)
