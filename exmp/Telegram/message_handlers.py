"""Функции связанные с обработкой текстовых сообщениий"""
import pprint

from django.db.models import Value, F, Q
from django.db.models.functions import Replace

from telebot.types import Message, ReplyKeyboardRemove

from ..models import TgUser, Group, Teacher
from ..Telegram.TgMain import send_message

from .. import utils
from ..logg import LoggEvent

from ..Less.ParseLessons import analisys_day, for_list
from ..Less.keyboards import (to_telegram_keyboard, choose_group_teacher_keyboard,
                              for_help_message_keyboard, schedule_keyboard,
                              step_by_step_day_keyboard, for_logs_pages, main_menu_keyboard)
from ..Less.ParseLogs import message_to_logs, stat_logs_by_resourse, get_log_by_id
from ..Less.TextConstants import (START_MESSAGE, HELP_MESSAGE_TG,
                                  GOOD_SET_RASP, IDONT_UNDERSTAND_GROUP, MENU_MESSAGE)

TYPE_LOGG = "TG"


def is_admin(func):
    """Проверка админки"""

    def wrapper(message: Message):
        """Проверочка"""
        tg_user = TgUser().create_or_update_user(message.from_user)
        if tg_user.is_admin:
            return func(message)

    return wrapper


def send_welcome(message: Message) -> None:
    """Стартовое сообщение пользователю"""

    tg_user = TgUser()
    user: TgUser = tg_user.create_or_update_user(message.from_user)
    send_message(message.chat.id, START_MESSAGE, reply_markup=to_telegram_keyboard(choose_group_teacher_keyboard()))
    LoggEvent("TG", message.chat.id, "StartMessage", message.chat.id)


def send_menu(message: Message) -> None:
    """Сообщение с меню"""
    send_message(message.chat.id, MENU_MESSAGE, reply_markup=to_telegram_keyboard(main_menu_keyboard()))


def send_help(message: Message) -> None:
    """Сообщение для команды помощь"""
    send_message(message.chat.id, HELP_MESSAGE_TG, reply_markup=to_telegram_keyboard(for_help_message_keyboard()))


def set_group_by_text(message: Message) -> None:
    """Назначение группы по текстовому вводу"""
    group_name = utils.replace_group(message.text)
    getgroup = Group.objects.filter(name__icontains=group_name).order_by("name")
    this_gr = getgroup.filter(name=group_name).first() if len(getgroup) > 1 else getgroup[0] if len(getgroup) == 1 else None
    if this_gr:
        user = TgUser().create_or_update_user(message.from_user)
        user.group = this_gr
        user.teacher = None
        user.save()

        send_message(message.chat.id, GOOD_SET_RASP.format(this_gr.title_name), reply_markup=to_telegram_keyboard(schedule_keyboard()))
        LoggEvent("TG", message.from_user.id, "SetGoodGroup", f"{this_gr.id}")
    else:
        tx_ = IDONT_UNDERSTAND_GROUP
        if len(getgroups := Group.objects.filter(name__icontains=group_name[:4])[:10]) > 0:
            tx_ += ", ".join(map(lambda ttl: "<code>" + ttl + "</code>", [gr.title_name for gr in getgroups]))
        else:
            tx_ = tx_.split('\n')[0]
        send_message(message.chat.id, tx_, reply_markup=to_telegram_keyboard(choose_group_teacher_keyboard()), parse="HTML")
        LoggEvent("TG", message.from_user.id, "BadGroup", f"{message.text}")


def give_schedule(message: Message) -> None:
    """Выдать расписание по запросу"""
    if message.__dict__.get('via_bot', None) != None:
        return None
    tg_user = TgUser().create_or_update_user(message.from_user)
    text_message, num_day = analisys_day(tg_user=tg_user)
    kb = to_telegram_keyboard(step_by_step_day_keyboard(num_day)) if num_day > -1 else to_telegram_keyboard(choose_group_teacher_keyboard())
    send_message(message.chat.id, text_message, reply_markup=kb)
    LoggEvent("TG", message.from_user.id, "Schedule", f"{message.chat.id}")


def clear_keyboard(message: Message) -> None:
    """Почистить клавиатуру"""
    send_message(message.chat.id, "Почистил", reply_markup=ReplyKeyboardRemove())


@is_admin
def give_logs_message(message: Message) -> None:
    """Обработчик логов"""
    text_message, pld, nxt, page = message_to_logs(message.text, "TG")
    send_message(message.chat.id, text_message, reply_markup=to_telegram_keyboard(for_logs_pages(pld, nxt, page)), parse="HTML")


@is_admin
def give_stats_message(message: Message) -> None:
    """Обработчик статистика"""
    text_message = stat_logs_by_resourse("TG", message.text)
    send_message(message.chat.id, text_message)


@is_admin
def give_logid_message(message: Message) -> None:
    """Обработчик поиска по айди"""
    if message.text.lower().replace('.лог', '').isdigit():
        mess = get_log_by_id(int(message.text.lower().replace('.лог', '')))
        send_message(message.chat.id, mess)
    else:
        send_message(message.chat.id, "ℹ️ Корректный запрос лог123")


@is_admin
def get_who_info_user(message: Message) -> None:
    """Узнать информацию о пользователях"""
    txt = message.text.split(' ', 1)[-1]
    users = TgUser.objects.filter(
        Q(user_id__icontains=txt) |
        Q(first_name__icontains=txt) |
        Q(last_name__icontains=txt) |
        Q(username__icontains=txt)
    )
    txt_message = "🔍 Что я нашёл:\n"
    if users:
        txt_message += f"📇 Количество {len(users)}\n\n"
        txt_message += "\n\n".join(map(lambda x: f"🆔 {x.user_id}\nℹ️ {"@" + x.username + " " if x.username else ""}{x.first_name + "" if x.first_name else ""} "
                                                 f"{x.last_name if x.last_name else ""}", users))
        if len(txt_message) > 4000:
            txt_message = txt_message[:4000] + "\n(Сокращено)"
    else:
        txt_message += "😔 Ничего :))"
    send_message(message.chat.id, txt_message)


def last_chance_message(message: Message):
    """Проверка является ли сообщение отправленное пользователем фамилией преподавателя"""
    teachers = None
    if message.text:
        teachers = Teacher.objects.annotate(
            title_name=Replace(Replace(Replace(Replace(F('name'), Value('доц.'), Value('')), Value('проф.'), Value('')), Value('ст.пр.'), Value('')), Value('асс.'), Value(''))
        ).filter(name__icontains=message.text.lower().replace('ё', 'е')).exclude(name="#").order_by('title_name')
    if teachers:
        txt_message, keyb = for_list(teachers[:4], _typ="teacher")
        send_message(message.chat.id, txt_message, reply_markup=to_telegram_keyboard(keyb))
    else:
        LoggEvent("TG", message.from_user.id, "AboutNothing", message.text.__str__() + (f" ({message.chat.id})" if message.chat.id != message.from_user.id else ""))
