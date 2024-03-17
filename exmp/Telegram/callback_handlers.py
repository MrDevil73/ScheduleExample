"""Callback telegram"""
from django.db.models import Value, F
from django.db.models.functions import Replace

from telebot.types import CallbackQuery

from ..models import TgUser, Teacher, Group

from .TgMain import edit_message, delete_message, send_message

from ..Less.ParseLessons import analisys_day, get_calls, for_week, for_list
from ..Less.TextConstants import MENU_MESSAGE, HELP_MESSAGE_TG, LIST_WEEK_DAYS, SHOW_RASP, GOOD_SET_RASP, LIST_COUNT, SHOW_CHOOSE
from ..Less.keyboards import (to_telegram_keyboard, choose_group_teacher_keyboard, main_menu_keyboard,
                              for_help_message_keyboard, to_menu_keyboard, week_keyboard, set_value, schedule_keyboard,
                              step_by_step_day_keyboard, for_logs_pages)
from ..Less.ParseLogs import message_to_logs

from ..logg import LoggEvent
from ..utils import get_time


def is_admin(func):
    """Проверка админки"""

    def wrapper(message: CallbackQuery):
        """Проверочка"""
        tg_user = TgUser().create_or_update_user(message.from_user)
        if tg_user.is_admin:
            return func(message)

    return wrapper


def parse_day_schedule(call: CallbackQuery) -> None:
    """Редактирование сообщения на расписание нужного дня"""
    number_day = int(call.data.split('_')[-1]) if call.data.split('_')[-1].isdigit() else 0
    tg_user = TgUser().create_or_update_user(call.from_user)
    text_message, num_day = analisys_day(number_day, tg_user)
    kb = to_telegram_keyboard(step_by_step_day_keyboard(num_day)) if num_day > -1 else to_telegram_keyboard(choose_group_teacher_keyboard())
    edit_message(call.message.chat.id, call.message.id, text_message, reply_markup=kb)
    LoggEvent("TG", call.from_user.id, "ScheduleButton", f"{call.message.chat.id}_{num_day}")


def edit_to_menu(call: CallbackQuery) -> None:
    """Редактирование сообщения на меню"""
    edit_message(call.message.chat.id, call.message.id, MENU_MESSAGE, reply_markup=to_telegram_keyboard(main_menu_keyboard()))


def edit_to_help(call: CallbackQuery) -> None:
    """Редактирование сообщения на сообщение с подсказкой"""
    edit_message(call.message.chat.id, call.message.id, HELP_MESSAGE_TG, reply_markup=to_telegram_keyboard(for_help_message_keyboard()))


def edit_to_calls(call: CallbackQuery) -> None:
    """Редактирование сообщения на расписание звонков"""
    edit_message(call.message.chat.id, call.message.id, get_calls(), reply_markup=to_telegram_keyboard(to_menu_keyboard()))


def edit_to_week(call: CallbackQuery) -> None:
    """Редактирование сообщения на выбор дня недели"""
    n_w = int(call.data.split('_')[-1])
    day_start = for_week(n_w)
    edit_message(call.message.chat.id, call.message.id, LIST_WEEK_DAYS.format([None, "текущей", "следующей"][n_w]), reply_markup=to_telegram_keyboard(week_keyboard(day_start)))


def ask_set_value(call: CallbackQuery) -> None:
    """Изменине сообщение на подвтерждение значения"""

    num_tc = call.data.split('_')
    if not num_tc[-1].isdigit():
        return None
    elem = None
    match num_tc[0]:
        case "teacher":
            elem = Teacher.objects.filter(id=int(num_tc[-1])).first()
            nm = elem.name
            val = "teacher"
        case "group":
            elem = Group.objects.filter(id=int(num_tc[-1])).first()
            nm = elem.title_name
            val = "group"
    if elem:
        ms = SHOW_RASP.format(nm)
        kb = to_telegram_keyboard(set_value(val, elem.id))
        edit_message(call.message.chat.id, call.message.id, ms, kb)


def set_value_callback(call: CallbackQuery) -> None:
    """Назначить человеку расписания группы или преподавателя"""
    num_tc = call.data.split('_')
    if not num_tc[-1].isdigit():
        return None
    tg_user = TgUser().create_or_update_user(call.from_user)
    if "teacher" in call.data:
        el = Teacher.objects.filter(id=int(num_tc[-1])).first()
        tp = "teacher"
    else:
        el = Group.objects.filter(id=int(num_tc[-1])).first()
        tp = "group"
    if el:
        ms = GOOD_SET_RASP.format(el.__dict__.get('title_name', el.name))
        tg_user.teacher = el if tp == "teacher" else None
        tg_user.group = el if tp == "group" else None
        tg_user.save()

        if (get_time() - call.message.date) < 44 * 60 * 60:
            delete_message(call.message.chat.id, call.message.id)
        else:
            edit_message(call.message.chat.id, call.message.id, "✅ Данные по вашему расписанию обновлены!", to_telegram_keyboard(to_menu_keyboard()))

        send_message(call.message.chat.id, ms, to_telegram_keyboard(schedule_keyboard()))

        LoggEvent("TG", call.from_user.id, "SetGoodGroup" if tp == "group" else "SetTeacherGood", f"{el.id}")


def get_list_elements(call: CallbackQuery) -> None:
    """Возвращает список элементов в клавишах по страницам"""

    pg = int(call.data.split('_')[-1])
    if "teacher" in call.data:
        query = Teacher.objects.annotate(
            title_name=Replace(Replace(Replace(Replace(F('name'), Value('доц.'), Value('')), Value('проф.'), Value('')), Value('ст.пр.'), Value('')), Value('асс.'), Value(''))
        ).exclude(name='#').order_by('title_name')[LIST_COUNT * pg:]
        _typ = "teacher"
    else:
        query = Group.objects.all().order_by('name')[LIST_COUNT * pg:]
        _typ = "group"
    elements = query

    mes, keyb = for_list(elements[:LIST_COUNT], bool(elements[LIST_COUNT:]), pg, _typ)
    edit_message(call.message.chat.id, call.message.id, mes, to_telegram_keyboard(keyb))


def give_choise(call: CallbackQuery) -> None:
    """Выбор преподаватель или группа"""
    edit_message(call.message.chat.id, call.message.id, SHOW_CHOOSE, to_telegram_keyboard(choose_group_teacher_keyboard()))


@is_admin
def edit_to_logs(call: CallbackQuery) -> None:
    """История логов по параметрам"""
    text_message, pld, nxt, page = message_to_logs(call.data, "TG")
    edit_message(call.message.chat.id, call.message.id, text_message, reply_markup=to_telegram_keyboard(for_logs_pages(pld, nxt, page)))
