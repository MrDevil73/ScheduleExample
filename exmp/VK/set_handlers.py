import re
from ..utils import replace_group
from .create_handlers import process_request, vkregister_callbackquery_handler, vkregister_message_handler

from .message_handlers import (send_welcome, send_help, give_schedule, set_group_by_text, last_chance_message,
                               give_logs_message, give_logid_message, give_stats_message, get_command_prepod, send_menu)

from .callback_handlers import (edit_to_menu, edit_to_help, edit_to_calls, edit_to_week,
                                give_choise, get_list_elements, ask_set_value, never_data, parse_day_schedule,
                                set_value_callback, edit_to_logs)

vkregister_message_handler(give_logs_message, regex=r'^\.логи')
vkregister_message_handler(give_logid_message, regex=r'^.лог[0-9]{0,20}')
vkregister_message_handler(give_schedule, regex="расп[0-9а-яА-ЯёЁ]{0,}")
vkregister_message_handler(send_menu, regex="(мен|men)[0-9а-яА-ЯёЁ]{0,}")
vkregister_message_handler(set_group_by_text,
                           lambda data: re.match(r'([0-9]{0,2}[а-яА-Я]{1,8}[0-9]{1,7}|[0-9]{2}[а-яА-Я]{1,4})',
                                                 replace_group(data.object.message.text)
                                                 )
                           )
vkregister_message_handler(send_welcome, regex="\/start|начать|start")
vkregister_message_handler(send_help, regex="(hel|пом|подс)[а-яА-Яa-zA-Z0-9]{0,8}")

vkregister_message_handler(give_stats_message, regex=r'^.стат')
vkregister_message_handler(get_command_prepod, regex=r'^преп')
vkregister_message_handler(last_chance_message, condition=lambda data: True)

vkregister_callbackquery_handler(parse_day_schedule, regex_data="getday_[0-9]{1,}")

vkregister_callbackquery_handler(edit_to_menu, regex_data="menu")
vkregister_callbackquery_handler(edit_to_help, regex_data="gethelp")
vkregister_callbackquery_handler(edit_to_calls, regex_data="calls")
vkregister_callbackquery_handler(edit_to_week, regex_data="^week")

vkregister_callbackquery_handler(give_choise, regex_data="^choiseteachgroup")
vkregister_callbackquery_handler(get_list_elements, regex_data="^list")
vkregister_callbackquery_handler(ask_set_value, condition=lambda data: data.event.payload.split('_')[0] in ['teacher', 'group'])
vkregister_callbackquery_handler(set_value_callback, regex_data="^set")
vkregister_callbackquery_handler(edit_to_logs, regex_data="^logs")

vkregister_callbackquery_handler(edit_to_menu, condition=lambda data: True)
