"""Файл со всеми функциями для красивого отображения текста лекций"""
from ..models import TgUser, Lesson, VkUser
from ..utils import get_time, numberday_to_date
from .TextConstants import *
from .keyboards import list_elements_keyboard

START_TIME = 1598832000
CONST_NEXT_DAY = (21 * 60 + 30) * 60


def good_ending(x) -> int:
    """Функция для правильной концовки часов,минут,секунд"""
    last_digit = x % 10
    last_two_digits = x % 100
    return 2 if 10 <= last_two_digits <= 20 or last_digit == 0 or 5 <= last_digit <= 9 else 0 if last_digit == 1 else 1


def number_to_smile(x: int) -> str:
    """Перевод числа в формат смайлика
    :param x: int Само число"""
    nms = "0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣".split(' ')
    return "".join([nms[int(i)] for i in str(x)])


def remain_time_func(granica, n_t, add_param=0) -> str:
    """Красивый текст с временем 'до'
    :param granica: Время до которого в считать (0-86399)
    :param n_t: Время сейчас
    :param add_param: Время которое необходимо добавить, если подсчёт в разных днях"""
    rem_message = ''
    remain_time = [int((granica - n_t + add_param) / 3600), int((granica - n_t + add_param) % 3600 / 60), int((granica - n_t + add_param) % 3600 % 60)]

    rem_message += f'{remain_time[0]} {["час", "часа", "часов"][good_ending(remain_time[0])]} ' if remain_time[0] else ""
    rem_message += f'{remain_time[1]} {["минута", "минуты", "минут"][good_ending(remain_time[1])]} ' if remain_time[1] else ""
    rem_message += f'{remain_time[2]} {["секунда", "секунды", "секунд"][good_ending(remain_time[2])]}\n'
    return rem_message


def how_remain(lessons: [], num_day: int, now_time: float, today: int):
    """Функция для возврата статуса занятий сейчас
    :param lessons: Занятия, необоходимы ключи time_start,time_finish
    :param num_day: День занятий
    :param now_time: Текущее мировое время
    :param today: Номер сегодняшнего дня"""
    now_day_time = now_time % 86400
    calls_k = {}
    message = ""

    def timestr_to_seconds(x: str) -> int:
        """Строка часов,минут в секунды"""
        ss = list(map(int, str(x).split(':')))
        return ((ss[0] * 60) + ss[1]) * 60

    for ls in lessons:
        calls_k[(timestr_to_seconds(ls.time_start), timestr_to_seconds(ls.time_finish))] = ls.order_in_day

    calls = list(calls_k.keys())

    if calls[-1][-1] <= now_day_time < CONST_NEXT_DAY:
        return FINISH_LESSONS + "\n"

    elif now_day_time >= CONST_NEXT_DAY and today + 1 == num_day or now_day_time < calls[0][0]:
        add_param = 0 if now_day_time < calls[0][0] else 86400 - now_day_time
        now_d_t = 0 if now_day_time > CONST_NEXT_DAY else now_day_time
        return LESSON_NOT_STARTED + "\n" + BEFORE_STARTS.format(calls_k[calls[0]], remain_time_func(calls[0][0], now_d_t, add_param))

    for elem in calls:
        if elem[0] <= now_day_time <= elem[1]:
            message += RIGHT_NOW.format(calls_k[elem]) + "\n"
            message += UNTIL_END.format(remain_time_func(elem[1], now_day_time))
            break
        elif elem[0] > now_day_time:
            break
    for ii in range(len(calls) - 1):
        if calls[ii][1] < now_day_time < calls[ii + 1][0]:
            if calls_k[calls[ii + 1]] - 1 == calls_k[calls[ii]]:
                message += BREAK_BETWEEN_LESSONS.format(calls_k[calls[ii]], calls_k[calls[ii + 1]]) + "\n"

            message += BEFORE_STARTS.format(calls_k[calls[ii]], remain_time_func(calls[ii + 1][0], now_day_time))
            break
    return message


def help_data_for_lessons(lessons: [], num_day: int) -> {}:
    """Возращает словарь с датами и статусом занятий"""
    answer = {}

    now_time = get_time()
    today = int(now_time // 86400) + 1
    answer['day'] = " на сегодня" if today == num_day else " на завтра" if today + 1 == num_day else ""
    answer['date_name'] = f"{['ср', 'чт', 'пт', 'сб', 'вск', 'пн', 'вт'][num_day % 7]}"
    answer['date'] = numberday_to_date(num_day)
    answer['head_info'] = ''
    if len(lessons) == 0:
        answer['head_info'] = NO_HAVE_LESSONS
        return answer

    if today == num_day or now_time % 86400 >= CONST_NEXT_DAY and num_day in [today, today + 1]:
        answer['head_info'] = how_remain(lessons, num_day, now_time, today)

    return answer


def get_less(num_day=19755, group=None, teacher=None):
    """По указанной группе или учителю, вернуть расписание для них"""
    if group:
        lessons = Lesson.objects.filter(number_day=num_day, group_id=group.id).prefetch_related('subgroup',
                                                                                                'teacher',
                                                                                                'audit',
                                                                                                'type').order_by('order_in_day',
                                                                                                                 'subgroup__name')
    else:
        lessons = Lesson.objects.filter(number_day=num_day, teacher_id=teacher.id).prefetch_related('subgroup', 'group', 'audit', 'type').order_by('order_in_day',
                                                                                                                                                   'subgroup__name')
    less = list(filter(lambda les: "коммент" not in les.type.name.lower(), lessons))
    coms = list(filter(lambda les: "коммент" in les.type.name.lower(), lessons))
    help_info = help_data_for_lessons(less, num_day)
    name_for = group.title_name if teacher is None else teacher.name
    text_message = MAIN_MESSAGE.format(name_for, help_info['day'], help_info['date_name'], help_info['date']) + "\n" * 2
    if help_info['head_info']:
        text_message += help_info['head_info']
    have_this = []
    prev_ord = 0
    is_wind = True
    for le in less:

        if le.order_in_day - 1 != prev_ord and le.order_in_day != prev_ord:
            for rr in range(prev_ord + 1, le.order_in_day):
                text_message += "\n" + f"{number_to_smile(rr)}" + f"{NEVER_LESSON if is_wind else WINDOW}" + "\n"

        if le.order_in_day != prev_ord:
            text_message += "\n" + f"{number_to_smile(le.order_in_day)}"
        if (lst := list(le.__dict__.values())[2:-1]) not in have_this:
            have_this.append(lst)
        else:
            continue
        text_message += "\n" + f"{le.subgroup.smile} ({le.subgroup.name.__str__()} группа) " if le.subgroup.name != 0 else ''
        text_message += f" {le.discipline}" + "\n"
        text_message += (f"{le.teacher.smile} {le.teacher.name.__str__()}" if teacher is None else f"{GROUP_SMILE} {le.group.title_name}") + "\n"
        if le.audit.name.__str__():
            text_message += f"{le.type.smile} {le.audit.name} " + (f"({le.type.name})" if str(le.type.name).lower() != 'none' else '') + "\n"
        text_message += START_STOP_TIME.format(le.time_start.__str__()[:-3], le.time_finish.__str__()[:-3]) + "\n"

        prev_ord = le.order_in_day
        is_wind = False

    text_message += f"\n"
    for cm in coms:
        text_message += f"{cm.type.smile} {cm.discipline}"

    return text_message


def for_list(elems, have_more=False, this_page=0, _typ="None") -> (str,):
    """Для красивого отображения переключателей"""
    txt_ = CHOOSE_TEACHER if _typ == "teacher" else CHOOSE_GROUP
    txt_ += CHOOSE_HELP
    prv, nxt = -1, -1
    if have_more:
        nxt = this_page + 1
        prv = -1
    if this_page > 0:
        prv = this_page - 1
    return txt_, list_elements_keyboard(elems, prv, nxt, _typ)


def for_week(n_w: int) -> int:
    """Возращает первый день недели, относительно номера недели который передан 1-текущий, 2-следующий"""
    ttime = get_time()
    number_day = int(ttime / 86400) + 1
    number_week = (ttime / 86400 + 3) % 7
    number_day += -(int(number_week))
    number_day += (n_w - 1) * 7
    return number_day


def analisys_day(number_day: int = None, tg_user: TgUser = None, vk_user: VkUser = None) -> (str, int):
    """Вычисляет номер дня, а так же возращает текст сообщеия с лекцияи"""

    if not number_day:
        ttime = get_time()
        number_day = int(ttime / 86400) + 1
        number_week = (ttime / 86400 + 3) % 7

        if HAVE_LESSONS_ON_SUNDAY is False and number_week > 5 + CONST_NEXT_DAY / 86400:
            number_day += (-(int(number_week)) + 7)
        elif number_week % 1 > CONST_NEXT_DAY / 86400:
            number_day += 1
    # Тут добавить о ВК
    main_message = ""
    if tg_user:
        if tg_user.group_id is None and tg_user.teacher_id is None:
            return UNKNOWN_GROUP_STATUS, -1
        main_message = get_less(number_day, tg_user.group, tg_user.teacher)
    elif vk_user:
        if vk_user.group_id is None and vk_user.teacher_id is None:
            return UNKNOWN_GROUP_STATUS, -1
        main_message = get_less(number_day, vk_user.group, vk_user.teacher)

    return main_message, number_day


def get_calls():
    """Возврат сообщения со звонками занятий"""
    cl_sp = CALLS_SPLIT.split('\n')
    text_message = CALLS_HEAD_MESSAGE + "\n" * 2
    for i, st in enumerate(cl_sp, start=1):
        text_message += f"{number_to_smile(i)} {st.strip()}" + "\n"
    return text_message
