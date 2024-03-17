"""Клавиатуры"""
import json
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from .TextConstants import (HAVE_LESSONS_ON_SUNDAY, GROUP_SMILE,
                            TEACHER_SMILE, CLOSE_SMILE, LEFT_SMILE,
                            RIGHT_SMILE, RELOAD_SMILE, SUCCESS_SMILE)


class ButtonCustom:
    """Кастомная кнопка"""
    payload = ""
    text_label = ""
    type_ = ""
    color = ""

    def __init__(self, text_label, payload=None, type_: str = "inline", color="primary"):
        self.text_label = text_label
        self.payload = payload
        self.type_ = type_
        self.color = color


class Keyb:
    """Кастомная клавиатура"""
    type_ = None
    buttons = []

    def __init__(self, type_):
        self.type_ = type_
        self.buttons = []


def to_vk_keyboard(kb: Keyb) -> {}:
    """Преобразование клавиатуры в формат VK"""
    if kb.buttons == [[]]:
        return ''

    def to_vk_button(label: str, payload: str, type_: str, color: str, ):
        """Создание кнопки вк"""
        type_ = "callback" if type_ == "inline" else type_
        payload = payload.replace("\"", "")
        but = {
            'color': color,
            'action': {
                'type': type_,
                'label': label,
                "payload": f"\"{payload}\""
            }
        }
        return but

    btn = [[to_vk_button(but.text_label, but.payload, but.type_, but.color) for but in kb.buttons[i]] for i in range(len(kb.buttons))]
    keyboardik = {
        'inline': kb.type_ == "inline",
        'buttons': btn
    }

    return json.dumps(keyboardik)


def to_telegram_keyboard(keyb: Keyb) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    """Преобразование клавиатуры в формат TG"""

    def to_telegram_button(but: ButtonCustom) -> InlineKeyboardButton | KeyboardButton:
        """Создание кнопки вк"""
        if but.type_ == "inline":
            return InlineKeyboardButton(text=but.text_label, callback_data=but.payload)
        else:
            return KeyboardButton(text=but.text_label)

    if keyb.type_ == "inline":
        ret_keyboard_main = InlineKeyboardMarkup()
        for but_arr in keyb.buttons:
            ret_keyboard_main.row(*[to_telegram_button(btn) for btn in but_arr])
        return ret_keyboard_main
    elif keyb.type_ == "text":
        ret_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
        for but_arr in keyb.buttons:
            ret_keyboard.row(*[to_telegram_button(btn) for btn in but_arr])
        return ret_keyboard


def menu_button() -> ButtonCustom:
    """Создание кнопки меню"""
    return ButtonCustom("Меню", "menu", "inline", "secondary")


def to_menu_keyboard() -> Keyb:
    """Клавиатура с одной кнопкой 'Меню'"""
    keyb = Keyb("inline")
    keyb.buttons.append([menu_button()])
    return keyb


def main_menu_keyboard() -> Keyb:
    """Основаная клавиатура меню"""
    keyb = Keyb("inline")
    btn = []
    btn.append([ButtonCustom("Расписание", "getday_0", "inline", "positive")])
    btn.append([ButtonCustom("Текущая неделя", "week_1", "inline", "secondary")])
    btn.append([ButtonCustom("Следующая неделя", "week_2", "inline", "secondary")])
    btn.append([ButtonCustom("Звонки", "calls", "inline", "secondary")])
    btn.append([ButtonCustom("Помощь", "gethelp", "inline", "primary")])
    keyb.buttons = btn

    return keyb


def schedule_keyboard() -> Keyb:
    """Клавиатура с кнопкой 'Расписание' в чате"""
    keyb = Keyb("text")
    keyb.buttons.append([ButtonCustom("Расписание", "getday_0", "text", "primary")])
    return keyb


def step_by_step_day_keyboard(now_day: int) -> Keyb | None:
    """Следующий и предыдующий день клавиатура"""

    if now_day <= 0:
        return None
    if HAVE_LESSONS_ON_SUNDAY:
        ppr, nxt = now_day - 1, now_day + 1
    else:
        if now_day % 7 == 3:
            ppr = now_day - 1
            nxt = now_day + 2
        elif now_day % 7 == 5:
            ppr = now_day - 2
            nxt = now_day + 1
        else:
            ppr = now_day - 1
            nxt = now_day + 1
    keyb = Keyb("inline")

    keyb.buttons.append([ButtonCustom("◀️ Предыдущий день", f"getday_{ppr}", "inline", "positive")])
    keyb.buttons.append([ButtonCustom("Следующий день ▶️", f"getday_{nxt}", "inline", "positive")])
    keyb.buttons.append([menu_button()])

    return keyb


def week_keyboard(day_start: int) -> Keyb:
    """Клавиатура с клавишами днями неделями
    :param day_start: Номер дня понедельника"""
    keyb = Keyb("inline")
    names_of_week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
    for el in range(0, 3):
        date_1 = time.gmtime((day_start + el * 2) * 86400 - 12 * 60 * 60)
        date_2 = time.gmtime((day_start + el * 2 + 1) * 86400 - 12 * 60 * 60)
        keyb.buttons.append([
            ButtonCustom(f"{date_1.tm_mday:02d}.{date_1.tm_mon:02d} {names_of_week[0 + el * 2].title()}", f"getday_{day_start + el * 2}", color="secondary"),
            ButtonCustom(f"{date_2.tm_mday:02d}.{date_2.tm_mon:02d} {names_of_week[1 + el * 2].title()}", f"getday_{day_start + el * 2 + 1}", color="secondary")
        ]
        )

    if HAVE_LESSONS_ON_SUNDAY:
        date_vsk = time.gmtime((day_start + 6) * 86400 - 12 * 60 * 60)
        keyb.buttons.append([ButtonCustom(f"{date_vsk.tm_mday:02d}.{date_vsk.tm_mon:02d} Воскресенье", f"getday_{day_start + 6}", color="secondary")])
    keyb.buttons.append([menu_button()])

    return keyb


def list_elements_keyboard(elems: list, prev: int = -1, nxt: int = -1, _typ: str = "None") -> Keyb:
    """Клавиатура со списком элементов
    :param elems: Элементы, которые необходимо отображать, необходим ключ title_name
    :param prev: Номер предыдущей страницы
    :param nxt: Номер следующей страницы
    :param _typ: Ключ значений которые передаются group/teacher"""
    keyb = Keyb("inline")

    for el in elems:
        keyb.buttons.append([ButtonCustom(f"{el.title_name}", f"{_typ}_{el.id}", color="secondary")])
    rw = []
    if prev > -1:
        rw.append(ButtonCustom(LEFT_SMILE, f"list{_typ}_{prev}"))
    rw.append(ButtonCustom(CLOSE_SMILE, "choiseteachgroup"))
    if nxt > -1:
        rw.append(ButtonCustom(RIGHT_SMILE, f"list{_typ}_{nxt}"))
    keyb.buttons.append(rw)

    return keyb


def choose_group_teacher_keyboard() -> Keyb:
    """Клавиатура с кнопками 'Группы','Преподаватели'"""
    keyb = Keyb("inline")
    keyb.buttons.append([ButtonCustom(f"{GROUP_SMILE} Группы", "listgroup_0")])
    keyb.buttons.append([ButtonCustom(f"{TEACHER_SMILE} Преподаватели", "listteacher_0")])
    keyb.buttons.append([menu_button()])
    return keyb


def for_help_message_keyboard() -> Keyb:
    """Клавиатура с кнопкой смены расписания"""
    keyb = Keyb("inline")
    keyb.buttons.append([ButtonCustom(f"{RELOAD_SMILE} Сменить расписание", f"choiseteachgroup")])
    keyb.buttons.append([menu_button()])
    return keyb


def set_value(val, _id) -> Keyb:
    """Клавиатура с подтверждением назначения параметра
    :param val: Параметр
    :param _id: Значение параметра"""
    keyb = Keyb("inline")
    keyb.buttons.append([ButtonCustom(f"{SUCCESS_SMILE} Да", f"set{val}_{_id}")])
    keyb.buttons.append([ButtonCustom(f"{CLOSE_SMILE} Нет", f"choiseteachgroup")])
    return keyb


def for_logs_pages(pld, nxt, page):
    """Клавиатура для пагинации"""
    keyb = Keyb("inline")
    buttons_row = []
    if page != 0:
        buttons_row.append(ButtonCustom(f"{LEFT_SMILE}", pld + f"{page - 1}"))
    if nxt:
        buttons_row.append(ButtonCustom(f"{RIGHT_SMILE}", pld + f"{page + 1}"))
    keyb.buttons = [buttons_row]
    return keyb
