import re
import sqlite3
import time
import os

from ..utils import get_time

categoryes = {"sysStart": "♻️ Запуск системы",
              "sysError": "❗️ Ошибка",
              "SetGoodGroup": "✏️Назначений групп",
              "BadGroup": "❓ Неудачное назначение",
              "StartMessage": "🖊 Нажатие начать",
              "ScheduleButton": "📨Запрос расписания клавиатурой",
              "Schedule": "✉️ Запрос расписания",
              "SetTeacherGood": "🧑‍🏫 Назначение преподавателем",
              "AboutNothing": "🚽 Сообщений ни о чём",
              "GetPrepod": "👨‍🏫 Пробив препода",
              "NewUser": "🥳 Новый пользователь",
              "InlineMessage": "🌐 Инлайн запрос"}

APP_NAME = __package__.split('.')[0].upper()
DB_FILENAME = os.getenv(f"{APP_NAME}_DB_FILENAME")
LOG_FILENAME = os.getenv(f"{APP_NAME}_LOG_FILENAME")
limit_page = 20


def ConCur(name=DB_FILENAME) -> (sqlite3.Cursor, sqlite3.Cursor):
    """Подключение к базе"""
    con = sqlite3.connect(name)
    cur = con.cursor()
    return con, cur


def arr_to_int(elements) -> []:
    """Костыль"""
    return [elements[0], int(elements[1]), int(elements[2]), elements[3], elements[4]]


def integrate_logs_to_db(name_file=LOG_FILENAME):
    """Интеграция строк из лог файла в базу"""
    tm = time.time()
    with open(name_file, mode='r', encoding='utf-8') as file:
        x = file.read()

    lgs = [arr_to_int(element.split(' | ')) for element in x.split('\n')[:-1] if re.match(r'[A-Z]{2,10}\s\|\s[0-9]{8,12}\s\|\s[0-9]{1,17}\s\|\s[a-zA-Z]{1,32}\s\|\s', element)]

    con, cur = ConCur()
    cur.executemany("""INSERT INTO logs VALUES (NULL,?,?,?,?,?)""", lgs)
    con.commit()

    with open(name_file, mode='w', encoding='utf-8') as file:
        file.close()
    return [time.time() - tm, len(lgs)]


def GetAllStats(how_hourse=0, resourse="TG"):
    """Возвращеие статистики по категории и часам"""
    con, cur = ConCur()
    add_to_sql = f" AND timestamp>{get_time() - how_hourse * 60 * 60} " if how_hourse else ""
    cur.execute(f"""SELECT category,count(*) FROM logs WHERE resourse="{resourse}" {add_to_sql} GROUP BY category ORDER by count(*) DESC """)
    results = cur.fetchall()
    cur.execute(f"""SELECT user_id,count(*) FROM logs WHERE resourse="{resourse}" {add_to_sql} GROUP BY user_id ORDER by count(*) DESC """)
    users = cur.fetchall()
    return results, users


def FilterLogs(user_id: list = None, categs: list = None, page=0, resourse="TG") -> [[]]:
    """Запрос к базе для получения логов"""
    sql_exp = f"""SELECT id,timestamp,user_id,category,message FROM logs WHERE (resourse="{resourse}" {'OR resourse="SYS"' if categs or 444 in user_id else ''}) """
    if user_id:
        users_str = " OR ".join(map(lambda x: "user_id=" + str(x), user_id))
        sql_exp += f"AND ({users_str})"

    if categs:

        add_el = " OR ".join(map(lambda x: "category='" + str(list(categoryes.keys())[x]) + "'", categs))
        if add_el:
            sql_exp += f" AND ({add_el})"
    sql_exp += f" ORDER BY timestamp DESC LIMIT {limit_page + 1} OFFSET {limit_page * int(page)}"
    con, cur = ConCur()
    cur.execute(sql_exp)
    return cur.fetchall()


def get_log_by_id(id_log):
    """Поиск айди лога"""
    con, cur = ConCur()
    sql_exp = f"SELECT * FROM logs WHERE id={id_log}"
    cur.execute(sql_exp)
    result = cur.fetchone()
    if result:
        mess = f"🔭 Лог по номеру {id_log}\n"
        mess += f"🗄 {result[1]}\n"
        mess += f"🕒 {time.strftime('%d.%m.%y %H:%M:%S', time.gmtime(result[2]))}\n"
        mess += f"👦 {result[3]}\n"
        mess += f"📓 {result[4]}\n"
        mess += f"📄 {result[5][:3980].replace(';;', '\n\n')}"
        return mess
    return f"🚫 Такого лога я не нашёл"


def stat_logs_by_resourse(resourse, mess) -> str:
    """Сообщение со статистикой по ресурсу и часам"""
    mess_split = mess.split(' ')

    how_hours = int(mess_split[1]) if len(mess_split) > 1 and mess_split[1].isdigit() else 0
    integrasion = integrate_logs_to_db()
    message = "📊 Статистика"
    message += f" за последние {how_hours} часа:\n\n" if how_hours else ":\n\n"
    if int(integrasion[1]) > 0:
        try:
            message += f"💿 Интеграция логов строк (VK+TG) {integrasion[1]}, {str(integrasion[0])[:6]} секунд\n"
        except:
            message += f"💿 Интеграция логов строк {integrasion[1]}, {integrasion[0]} секунд\n"
    get_stat, users__ = GetAllStats(how_hours, resourse)  # list(reversed(sorted(GetAllStats(how_hours), key=lambda x:x[1])))
    all_sum = sum([x[1] for x in get_stat])
    message += f"💾 Всего запросов {all_sum}\n"
    message += f"🚶‍♂️ Уникальных пользователей {len(users__)}\n\n"
    for elem in get_stat:
        message += f"""{elem[0]}: {elem[1]}\n"""
    for kl in categoryes.keys():
        message = message.replace(kl, categoryes[kl])
    return message


def beautiful_logs(user_id: list = None, categs: list = None, page=0, resourse="TG") -> (str, bool):
    """Красивое отображение логов"""
    logs = FilterLogs(user_id, categs, page, resourse)
    message = "🗃 Запрос логов:\n"
    if categs:
        message += "\n⚙️ Категории: " + ",".join(list(set([list(categoryes.keys())[k] for k in categs])))
    if user_id:
        message += "\n👯 Пользователи: " + ",".join(map(str, user_id))
    if page:
        message += f"\n📃 Страница: {page}"
    message += "\n"
    for el in reversed(logs[:20]):
        message += f"[{time.strftime('%d.%m %H:%M:%S', time.gmtime(el[1]))}] - "
        if user_id and len(user_id) == 1:
            pass
        else:
            message += f"<code>{el[2]}</code> - " if resourse == "TG" else f"{el[2]} - "
        message += f"{el[3]} - "
        message += f"{el[4].replace('<', '').replace('>', '')}" if len(el[4]) < 100 else f"лог{el[0]}"
        message += "\n"
    if len(logs) == 0:
        message += "👣 Логи по данным параметрам пусты"
    bool_next = True if len(logs) > limit_page else False
    return message, bool_next


def hlp_message():
    """Дополнительное сообщение помощи в логах"""
    ans = """🔨 Для запроса логов нужно ввести команду:
🔒 логи (ids) (categoryes) (page)
Пользователи и категории могут принимать несколько параметров, разделять следует запятыми.Если не нужен параметр - укажи 00
📜 Список доступных категорий по номерам\n"""
    for i, elem in enumerate(list(categoryes.keys())):
        if not elem.startswith("sys"):
            ans += f"{categoryes[elem]} - {i}\n"
    return ans


def message_to_logs(mess: str, resource="TG"):
    """Возвращает сообщение, пейлоад, наличие ещё страницы, текущую страницу"""
    if "пом" in mess:
        messag = hlp_message()
        return messag, f"none", False, 0
    integrate_logs_to_db()
    mess_split = mess.split(' ') if not mess.startswith("logs") else mess.split("_")
    user_id, categ, page = [], [], 0
    if len(mess_split) > 1:
        user_id = list(filter(None, map(lambda el: int(el) if el.isdigit() and el != "00" else "", mess_split[1].split(','))))
    if len(mess_split) > 2:
        categ = list(filter(lambda el: el != "" and el < len(categoryes.keys()), map(lambda el: int(el) if el.isdigit() and el != "00" else "", mess_split[2].split(','))))
    if len(mess_split) > 3:
        page = int(mess_split[3]) if mess_split[3].isdigit() else 0
    messag, bool_next = beautiful_logs(user_id, categ, page, resource)

    return messag, f"logs_{','.join(list(map(str, user_id)))}_{','.join(list(map(str, categ)))}_", bool_next, page
