"""Назначение обработчиков"""
import re

from .TgMain import bot

from .message_handlers import (send_welcome, send_help, set_group_by_text, give_schedule, clear_keyboard, last_chance_message, give_logs_message,
                               give_stats_message, give_logid_message, get_who_info_user, send_menu)
from .callback_handlers import (edit_to_calls, edit_to_help, edit_to_menu,
                                parse_day_schedule, edit_to_week, ask_set_value, set_value_callback, get_list_elements, give_choise, edit_to_logs)
from .inline_handlers import inline_func

from .. import utils

bot.register_message_handler(lambda x: x, func=lambda mes: mes.content_type in ['new_chat_members', 'left_chat_member'])


bot.register_message_handler(give_logs_message, regexp=r'^.логи')
bot.register_message_handler(give_schedule, regexp=r"расп[0-9а-яА-ЯёЁ]{0,}")
bot.register_message_handler(send_menu, regexp=r"(мен|men)[0-9а-яА-ЯёЁ]{0,}")
bot.register_message_handler(set_group_by_text, func=lambda message: re.match(r'([0-9]{0,2}[а-яА-Я]{1,8}[0-9]{1,7}|[0-9]{2}[а-яА-Я]{1,4})', utils.replace_group(message.text)))
bot.register_message_handler(send_welcome, func=lambda message: message.text and message.text.lower() in ['start', '/start', 'начать'])
bot.register_message_handler(send_help, regexp=r'(hel|пом|подс)[а-яА-Яa-zA-Z0-9]{0,8}')
bot.register_message_handler(clear_keyboard, regexp=r"clear")
bot.register_message_handler(get_who_info_user, regexp=r'^.who')
bot.register_message_handler(give_logid_message, regexp=r'^.лог[0-9]{0,20}')
bot.register_message_handler(give_stats_message, regexp=r'^.стат')

bot.register_callback_query_handler(parse_day_schedule, func=lambda call: call.data.startswith('getday'))

bot.register_callback_query_handler(edit_to_menu, func=lambda call: call.data == "menu")
bot.register_callback_query_handler(edit_to_help, func=lambda call: call.data == "gethelp")
bot.register_callback_query_handler(edit_to_calls, func=lambda call: call.data == "calls")
bot.register_callback_query_handler(edit_to_week, func=lambda call: call.data.startswith('week'))

bot.register_callback_query_handler(give_choise, func=lambda call: call.data.startswith('choiseteachgroup'))
bot.register_callback_query_handler(get_list_elements, func=lambda call: call.data.startswith('list'))
bot.register_callback_query_handler(ask_set_value, func=lambda call: call.data.split('_')[0] in ['teacher', 'group'])
bot.register_callback_query_handler(set_value_callback, func=lambda call: call.data.startswith('set'))
bot.register_callback_query_handler(edit_to_logs, func=lambda call: call.data.startswith('logs'))
bot.register_callback_query_handler(edit_to_menu, func=lambda call: True)

bot.register_inline_handler(inline_func, func=lambda call: call)

bot.register_message_handler(last_chance_message)
# logger.debug("Start Telegram bot",extra={'type': 'TG', 'user_id': 444, 'category': "StartBotPool"})
