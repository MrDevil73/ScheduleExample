
# Боты для расписания


Проект расчитан на тех людей кто чуть разбирается в Django (позже оберну докером)

Код для ботов расписания занятий (ВК и Телеграмм)

Немного асинхронщины и аккуратный код

* Python 3.13 
* Django 5.0.1

## Файл .env 

**{APP_NAME}** - название приложения в параметрах, например EXMP_TOKEN_TG

Должен содержать:
* {APP_NAME}_TOKEN_TG (Токен авторизации для Телеграмм)
* {APP_NAME}_SECRET_TOKEN_TG (Секретный ключ для запросов от Телеграмм в загаловке 'X-Telegram-Bot-Api-Secret-Token')
* MY_TELEGRAM_ID  (Ваш телеграмм айди куда будут приходит сообщения о ошибках(вдруг))

* {APP_NAME}_TOKEN_VK  (Токен для бота ВК)
* {APP_NAME}_SECRET_TOKEN_VK (Секретный ключ для запросов от ВК)
* {APP_NAME}_VK_RESPONSE  (Ключ для подтверждения сервера ВК)

* {APP_NAME}_LOG_FILENAME  (АБСОЛЮТНЫЙ ПУТЬ к файлу с логами)

* {APP_NAME}_DB_FILENAME  (АБСОЛЮТНЫЙ ПУТЬ к файлу с базой данных логов)

***
* HOST_DATABASE (Хост базы данных)
* PORT_DATABASE (Порт базы данных)
* NAME_DATABASE (Название необхидмой базы)
* USER_DATABASE (Пользователь базы данных)
* PASSWORD_DATABASE (Пароль базы данных)

В примере используется база данных - PostgreSQL
***

## Запуск приложения
1. Создания миграции к нужному приложению

```python manage.py makemigration exmp```

2. Применение миграций

```python manage.py migrate```

3. Запуск сервера

```python manage.py runserver```

## Данные
Для того чтобы внести данные в базу вы можете написать свой скрипт, или же вносить данные в exmp/storage/list.db и запустить скрипт в exmp/Integration/integrate_lessons.py

Скрипт сам создат аудитории, преподавателей, группу, подгруппу если их нет в базе данных

Необходимые данные
* ```number_day```	номер дня = ```(Время в unix)//(86400) + 1``` Пример: 17.03.2024 - 19800 (1710705078)
* ```order_in_day```	порядковый номер занятия в течении дня
* ```group_name```	Название группы (в базе учитываются лишь слеши)
* ```subgroup```      Подгруппа (по умолчанию ставить 0)
* ```discipline``` Название предмета
* ```type``` Тип - Зачёт/Лаборатоное занятие/Лекция
* ```smile``` Костыль который забыл убрать
* ```teacher``` Учитель (ЧУВСТВИТЕЛЕН К РЕГИСТРУ)
* ```audit``` Название аудитории
* ```time_start``` Время начала в формате HH:MM
* ```time_finish``` Время конца в формате HH:MM

Перейдите в папку exmp/Integration  и запустите скрипт ```python integrate_lessons.py```