from .VkMain import send_message, edit_message, user_get
from .types import Update

from ..Less.TextConstants import MENU_MESSAGE, HELP_MESSAGE_VK, LIST_WEEK_DAYS, SHOW_RASP, GOOD_SET_RASP, LIST_COUNT, SHOW_CHOOSE
from ..Less.keyboards import (to_vk_keyboard, choose_group_teacher_keyboard,
                              step_by_step_day_keyboard, main_menu_keyboard, for_help_message_keyboard,
                              to_menu_keyboard, week_keyboard, set_value, schedule_keyboard, for_logs_pages)
from ..Less.ParseLessons import get_calls, for_week, for_list, analisys_day

from .types import UserFromGet
from ..logg import LoggEvent
from ..models import Teacher, Group, VkUser
from django.db.models import Value, F
from django.db.models.functions import Replace
from ..Less.ParseLogs import message_to_logs

from asgiref.sync import sync_to_async


def is_admin(func):
    """Проверка админки"""

    async def wrapper(data: Update):
        """Проверочка"""

        @sync_to_async
        def get_user(data: Update):
            vk_user = VkUser().create_or_update_user(UserFromGet(data.event.user_id,
                                                                 "", "", ""))
            return vk_user

        vk_user = await get_user(data)
        if vk_user.is_admin:
            return await func(data)

    return wrapper


async def edit_to_menu(data: Update) -> None:
    """Редактирование сообщения на меню"""
    await edit_message(data.event.peer_id, data.event.conversation_message_id, MENU_MESSAGE, reply_markup=to_vk_keyboard(main_menu_keyboard()))


async def edit_to_help(data: Update) -> None:
    """Редактирование сообщения на сообщение с подсказкой"""

    await edit_message(data.event.peer_id, data.event.conversation_message_id, HELP_MESSAGE_VK, reply_markup=to_vk_keyboard(for_help_message_keyboard()))


async def edit_to_calls(data: Update) -> None:
    """Редактирование сообщения на расписание звонков"""

    await edit_message(data.event.peer_id, data.event.conversation_message_id, get_calls(), reply_markup=to_vk_keyboard(to_menu_keyboard()))


async def edit_to_week(data: Update) -> None:
    """Редактирование сообщения на выбор дня недели"""
    n_w = int(data.event.payload.split('_')[-1])
    day_start = for_week(n_w)

    await edit_message(data.event.peer_id,
                       data.event.conversation_message_id,
                       LIST_WEEK_DAYS.format([None, "текущей", "следующей"][n_w]),
                       reply_markup=to_vk_keyboard(week_keyboard(day_start)))


@sync_to_async
def parse_day_schedule_addon(user_id, number_day):
    vk_user = VkUser().create_or_update_user(UserFromGet(user_id, "", "", "", ))
    return analisys_day(number_day, vk_user=vk_user)


async def parse_day_schedule(data: Update) -> None:
    """Редактирование сообщения на расписание нужного дня"""
    number_day = int(data.event.payload.split('_')[-1]) if data.event.payload.split('_')[-1].isdigit() else 0
    text_message, num_day = await parse_day_schedule_addon(data.event.user_id, number_day)
    kb = to_vk_keyboard(step_by_step_day_keyboard(num_day)) if num_day > -1 else to_vk_keyboard(choose_group_teacher_keyboard())
    await edit_message(data.event.peer_id, data.event.conversation_message_id, text_message, reply_markup=kb)
    LoggEvent("VK", data.event.user_id, "ScheduleButton", f"{data.event.peer_id}_{number_day}")


@sync_to_async
def for_list_addon(data):
    pg = int(data.event.payload.split('_')[-1])
    if "teacher" in data.event.payload:
        query = Teacher.objects.annotate(
            title_name=Replace(Replace(Replace(Replace(F('name'), Value('доц.'), Value('')), Value('проф.'), Value('')), Value('ст.пр.'), Value('')), Value('асс.'), Value(''))
        ).exclude(name='#').order_by('title_name')[LIST_COUNT * pg:]
        _typ = "teacher"
    else:
        query = Group.objects.all().order_by('name')[LIST_COUNT * pg:]
        _typ = "group"
    elements = query

    mes, keyb = for_list(elements[:LIST_COUNT], bool(elements[LIST_COUNT:]), pg, _typ)
    return mes, keyb


async def get_list_elements(data: Update) -> None:
    """Возвращает список элементов в клавишах по страницам"""
    mes, keyb = await for_list_addon(data)

    await edit_message(data.event.peer_id, data.event.conversation_message_id, mes, to_vk_keyboard(keyb))


@sync_to_async
def ask_set_value_addon(data: Update):
    num_tc = data.event.payload.split('_')
    if not num_tc[-1].isdigit():
        return None

    match num_tc[0]:
        case "teacher":
            elem = Teacher.objects.filter(id=int(num_tc[-1])).first()
            nm = elem.name
            val = "teacher"
        case "group":
            elem = Group.objects.filter(id=int(num_tc[-1])).first()
            nm = elem.title_name
            val = "group"
        case _:
            elem, nm, val = None, None, None
    return elem, nm, val


async def ask_set_value(data: Update) -> None:
    """Изменине сообщение на подвтерждение значения"""

    elem, nm, val = await ask_set_value_addon(data)
    if elem:
        ms = SHOW_RASP.format(nm)
        kb = to_vk_keyboard(set_value(val, elem.id))
        await edit_message(data.event.peer_id,
                           data.event.conversation_message_id, ms, kb)


async def give_choise(data: Update) -> None:
    """Выбор преподаватель или группа"""
    await edit_message(data.event.peer_id,
                       data.event.conversation_message_id, SHOW_CHOOSE, to_vk_keyboard(choose_group_teacher_keyboard()))


@sync_to_async
def set_value_callback_addon(data: Update) -> None:
    num_tc = data.event.payload.split('_')
    if not num_tc[-1].isdigit():
        return None
    ms = "Ошибка"
    if "teacher" in data.event.payload:
        el = Teacher.objects.filter(id=int(num_tc[-1])).first()
        tp = "teacher"
    else:
        el = Group.objects.filter(id=int(num_tc[-1])).first()
        tp = "group"
    if el:
        vk_user = VkUser().create_or_update_user(UserFromGet(data.event.user_id, "", "", "", ))
        ms = GOOD_SET_RASP.format(el.__dict__.get('title_name', el.name))
        vk_user.teacher = el if tp == "teacher" else None
        vk_user.group = el if tp == "group" else None
        vk_user.save()
        LoggEvent("VK", data.event.user_id, "SetGoodGroup" if tp == "group" else "SetTeacherGood", f"{el.id}")
    return ms


async def set_value_callback(data: Update) -> None:
    """Назначить человеку расписания группы или преподавателя"""
    ms = await set_value_callback_addon(data)
    # delete_message(data.event.peer_id, data.event.conversation_message_id)
    await edit_message(data.event.peer_id, data.event.conversation_message_id, ms, to_vk_keyboard(schedule_keyboard()))


@is_admin
async def edit_to_logs(data: Update) -> None:
    text_message, pld, nxt, page = message_to_logs(data.event.payload, "VK")
    await edit_message(data.event.peer_id, data.event.conversation_message_id, text_message, reply_markup=to_vk_keyboard(for_logs_pages(pld, nxt, page)))


@sync_to_async
def never_data(data: Update):
    pass
