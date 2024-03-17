"""Inline handlers for Telegram"""
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineQuery

from ..models import TgUser, Group, Teacher

from .TgMain import inline_message

from ..Less.ParseLessons import analisys_day

from .. import utils
from ..logg import LoggEvent


def inline_func(call: InlineQuery) -> None:
    """Парсинг событий в других чатах через @"""

    logo = ["https://avatars.mds.yandex.net/i?id=052cfaf299d6993a5f75708f0dc937882fff3a58-5283588-images-thumbs&n=13",
            "https://cdn1.iconfinder.com/data/icons/rounded-social-media/512/telegram-1024.png"]
    tg_user = TgUser().create_or_update_user(call.from_user)
    elem = None
    if call.query:
        tp = "group"
        elem = Group.objects.filter(name__icontains=utils.replace_group(call.query)).first()
        if elem == None:
            elem = Teacher.objects.filter(name__icontains=call.query.lower()).exclude(name="#").first()
            tp = "teacher"
    ara = []
    if tg_user.group or tg_user.teacher:
        name = tg_user.group.title_name if tg_user.group else tg_user.teacher.name
        numb_day = int(utils.get_time() // 86400) + 1
        txt_1, num_day = analisys_day(numb_day, tg_user=tg_user)
        ara.append(InlineQueryResultArticle('0',
                                            name,
                                            description=f'на сегодня ({utils.numberday_to_date(num_day)})',
                                            input_message_content=InputTextMessageContent(message_text=txt_1),
                                            thumbnail_url=logo[0]))

        txt_2, num_day2 = analisys_day(tg_user=tg_user, number_day=num_day + 1)
        ara.append(InlineQueryResultArticle('1',
                                            name,
                                            description=f'на завтра ({utils.numberday_to_date(num_day2)})',
                                            input_message_content=InputTextMessageContent(message_text=txt_2),
                                            thumbnail_url=logo[0]))
    if elem is not None:
        tg_temp_user = TgUser()
        tg_temp_user.group = elem if tp == "group" else None
        tg_temp_user.teacher = elem if tp == "teacher" else None
        name2 = tg_temp_user.group.title_name if tg_temp_user.group else tg_temp_user.teacher.name
        numb_day = int(utils.get_time() // 86400) + 1
        txt_1, num_day = analisys_day(numb_day, tg_user=tg_temp_user)
        ara.append(InlineQueryResultArticle('3',
                                            name2,
                                            description=f'на сегодня ({utils.numberday_to_date(num_day)})',
                                            input_message_content=InputTextMessageContent(message_text=txt_1),
                                            thumbnail_url=logo[0]))

        txt_2, num_day2 = analisys_day(tg_user=tg_temp_user, number_day=num_day + 1)
        ara.append(InlineQueryResultArticle('4',
                                            name2,
                                            description=f'на завтра ({utils.numberday_to_date(num_day2)})',
                                            input_message_content=InputTextMessageContent(message_text=txt_2),
                                            thumbnail_url=logo[0]))

    ara.append(InlineQueryResultArticle('5',
                                        'Поделиться ботом',
                                        description="",
                                        input_message_content=InputTextMessageContent("🌐 Бот для получения расписания УлГУ для групп и "
                                                                                      "преподавателей! \nt.me/ulsurobot"),
                                        thumbnail_url=logo[1]))
    inline_message(call.id, ara)
    LoggEvent("TG", call.from_user.id, "InlineMessage", call.query)
