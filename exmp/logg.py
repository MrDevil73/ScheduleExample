import logging
from .utils import get_time
from .Less.ParseLogs import LOG_FILENAME

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')


class CustomFormatter(logging.Formatter):
    """Мой класс"""

    def format(self, record):
        """Запись события в файл логов"""
        timestamp = int(get_time())
        log_format = f"{record.resourse} | {timestamp} | {record.user_id} | {record.category} | {record.msg}"
        return log_format




file_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)


def LoggEvent(resourse, user_id, category, message):
    """Функция логирования"""
    logger.info(message, extra={'resourse': resourse, 'user_id': user_id, 'category': category})


LoggEvent("SYS", 444, "sysStart", "Start application")
