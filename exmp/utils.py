import time


def replace_group(group_text: str) -> str:
    """
    :param group_text:
    :return: Название группы для корректного поиска
    """
    group_text=str(group_text).lower()
    kostil_group = {'атпп': 'атп', '-0-': '-о-', 'иб-': 'ибас-', 'нттс-': 'нтс-'}
    for elem in kostil_group:
        group_text = group_text.replace(elem, kostil_group[elem])
    group_text = group_text.lower().replace(' ', '').replace('-', '').replace('ё', 'е')

    return group_text

def get_time() -> float:
    """:return: Возврат текущего времени"""
    return time.time() + 4 * 60 * 60


def numberday_to_date(num_day: int) -> str:
    """Преобразование номер дня в дату
    :num_day: Номер дня
    :return: Возвращает дату в формате ДД.ММ"""
    date_ = time.localtime(num_day * 86400 - 12 * 3600)
    return f"{date_.tm_mday:02d}.{date_.tm_mon:02d}"

def replace_from_lat(txt:str)->str:
    """Преобразование строки с английским алфавитом в русский
    :param txt: Входная строка
    :return: Исправленная строка"""
    latin_to_cyrillic = {
        'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н', 'K': 'К', 'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т',
        'X': 'Х', 'a': 'а', 'b': 'в', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х'
    }
    return txt.translate(str.maketrans(latin_to_cyrillic))