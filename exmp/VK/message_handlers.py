from asgiref.sync import sync_to_async

from .VkMain import send_message, user_get
from .types import Update, UserFromGet

from ..Less.TextConstants import START_MESSAGE, HELP_MESSAGE_VK, GOOD_SET_RASP, IDONT_UNDERSTAND_GROUP, MENU_MESSAGE
from ..Less.keyboards import (to_vk_keyboard, choose_group_teacher_keyboard,
                              step_by_step_day_keyboard,
                              for_help_message_keyboard, schedule_keyboard, for_logs_pages, main_menu_keyboard)
from ..Less.ParseLessons import analisys_day, for_list

from .. import utils

from ..models import VkUser, Teacher, Group

from django.db.models import Value, F
from django.db.models.functions import Replace

from ..logg import LoggEvent

from ..Less.ParseLogs import message_to_logs, stat_logs_by_resourse, get_log_by_id


def is_admin(func):
    """Проверка админки"""

    async def wrapper(data: Update):
        """Проверочка"""

        @sync_to_async
        def user(data: Update):
            vk_user = VkUser().create_or_update_user(UserFromGet(data.object.message.from_id,
                                                                 "", "", ""))
            return vk_user

        vk_user = await user(data)
        if vk_user.is_admin:
            return await func(data)

    return wrapper


async def send_welcome(data: Update):
    await send_message(data.object.message.peer_id, START_MESSAGE, to_vk_keyboard(choose_group_teacher_keyboard()))
    LoggEvent("VK", data.object.message.from_id, "StartMessage", data.object.message.peer_id)


async def send_help(data: Update) -> None:
    """Сообщение для команды помощь"""
    await send_message(data.object.message.peer_id, HELP_MESSAGE_VK, reply_markup=to_vk_keyboard(for_help_message_keyboard()))


async def send_menu(data: Update) -> None:
    """Сообщение меню"""
    await send_message(data.object.message.peer_id, MENU_MESSAGE, reply_markup=to_vk_keyboard(main_menu_keyboard()))


@sync_to_async
def give_schedule_addon(data: Update):
    vk_user = VkUser().create_or_update_user(UserFromGet(data.object.message.from_id, "", "", ""))
    return analisys_day(vk_user=vk_user)


async def give_schedule(data: Update) -> None:
    """Выдать расписание по запросу"""

    text_message, num_day = await give_schedule_addon(data)
    kb = to_vk_keyboard(step_by_step_day_keyboard(num_day)) if num_day > -1 else to_vk_keyboard(choose_group_teacher_keyboard())
    await send_message(data.object.message.peer_id, text_message, reply_markup=kb)
    LoggEvent("VK", data.object.message.from_id, "Schedule", f"{data.object.message.peer_id}")


@sync_to_async
def set_group_by_text_addon(group_name, user_id):
    getgroup = Group.objects.filter(name__icontains=group_name).order_by("name")
    this_gr = getgroup.filter(name=group_name).first() if len(getgroup) > 1 else getgroup[0] if len(getgroup) == 1 else None
    if this_gr:
        user = VkUser().create_or_update_user(UserFromGet(user_id, "", "", ""))
        user.group = this_gr
        user.teacher = None
        user.save()
        LoggEvent("VK", user_id, "SetGoodGroup", f"{this_gr.id}")
        return GOOD_SET_RASP.format(this_gr.title_name), to_vk_keyboard(schedule_keyboard())

    else:
        tx_ = IDONT_UNDERSTAND_GROUP
        if len(getgroups := Group.objects.filter(name__icontains=group_name[:4])[:10]) > 0:
            tx_ += ", ".join([gr.title_name for gr in getgroups])
        else:
            tx_ = tx_.split('\n')[0]
        LoggEvent("VK", user_id, "BadGroup", f"{group_name}")
        return tx_, to_vk_keyboard(choose_group_teacher_keyboard())


async def set_group_by_text(data: Update) -> None:
    """Назначение группы по текстовому вводу"""
    group_name = utils.replace_group(data.object.message.text)
    tx_, keyb = await set_group_by_text_addon(group_name, data.object.message.from_id)

    await send_message(data.object.message.peer_id, tx_, reply_markup=keyb)


@sync_to_async
def last_chance_message_addon(data: Update):
    teachers = Teacher.objects.annotate(
        title_name=Replace(Replace(Replace(Replace(F('name'), Value('доц.'), Value('')), Value('проф.'), Value('')), Value('ст.пр.'), Value('')), Value('асс.'), Value(''))
    ).filter(name__icontains=data.object.message.text.lower().replace('ё', 'е')).order_by('title_name')
    return teachers, bool(teachers)


async def last_chance_message(data: Update) -> None:
    """Проверка является ли сообщение отправленное пользователем фамилией преподавателя"""
    bl = None
    if data.object.message.text:
        teachers, bl = await last_chance_message_addon(data)
    if bl:
        txt_message, keyb = for_list(teachers[:4], _typ="teacher")
        await send_message(data.object.message.peer_id, txt_message, reply_markup=to_vk_keyboard(keyb))
    else:
        LoggEvent("VK", data.object.message.from_id, "AboutNothing", data.object.message.text)


@is_admin
async def give_logs_message(data: Update) -> None:
    """Обработчик логов"""
    text_message, pld, nxt, page = message_to_logs(data.object.message.text, "VK")
    await send_message(data.object.message.peer_id, text_message, reply_markup=to_vk_keyboard(for_logs_pages(pld, nxt, page)))


@is_admin
async def give_stats_message(data: Update) -> None:
    """Обработчик статистика"""
    text_message = stat_logs_by_resourse("VK", data.object.message.text)
    await send_message(data.object.message.peer_id, text_message)


@is_admin
async def give_logid_message(data: Update) -> None:
    """Обработчик поиска по айди"""
    if data.object.message.text.lower().replace('.лог', '').isdigit():
        mess = get_log_by_id(int(data.object.message.text.lower().replace('.лог', '')))
    else:
        mess = "ℹ️ Корректный запрос лог123"
    await send_message(data.object.message.peer_id, mess)


async def get_command_prepod(data: Update) -> None:
    txt = data.object.message.text.split(' ', 1)[-1]
    mess = get_prepod(txt)
    await send_message(data.object.message.peer_id, mess)
