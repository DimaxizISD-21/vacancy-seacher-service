import asyncio
import os, sys
import datetime

# Делаем парсер видимым для Django
project = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project)
os.environ['DJANGO_SETTINGS_MODULE'] = "vacancy_seacher.settings"

import django
django.setup()
from django.db import DatabaseError
from django.contrib.auth import get_user_model

from scraping.scrapper import *
from scraping.models import Vacancy, Error, Url


parsers = (
    (work_ua_parser, 'work'),
    (rabota_ua_parser, 'rabota'),
    (dou_ua_parser, 'dou'),
    (djinni_parser, 'djinni')
)

# Импортируем модель User
user = get_user_model()

jobs, errors = [], []

# Ф-ция получения настроек по умолчанию для текущего пользователя с
# уникальными набором города и языка програмирования
def get_user_settings():
    qs = user.objects.filter(send_email=True).values()
    settings_list = set((q['city_id'], q['language_id']) for q in qs)
    return settings_list

# Ф-ция вывода списка url
def get_urls(_settings):
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        if pair in url_dict:
            tmp = {}
            tmp['city'] = pair[0]
            tmp['language'] = pair[1]
            tmp['url_data'] = url_dict[pair]
            urls.append(tmp)
    return urls

# Ф-ция запуска парсера в асинхронном режиме
async def main(value):
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    jobs.extend(job)

user_settings = get_user_settings()
url_list = get_urls(user_settings)


# Создание цикла для запуска задач в асинхронном режиме
loop = asyncio.get_event_loop()

# Список задач
tmp_tasks = [(func, data['url_data'][key], data['city'], data['language'])
             for data in url_list
             for func, key in parsers]

# Запуск задач на выполнение
tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])

# # Перебор данных пользователей
# for data in url_list:
#     # Вызов ф-ций парсеров для своих url
#     for func, key in parsers:
#         url = data['url_data'][key]
#         j, e = func(url, city=data['city'], language=data['language'])
#         jobs += j
#         errors += e

loop.run_until_complete(tasks)
loop.close()


# Запись всех вакансий в БД
for job in jobs:
    v = Vacancy(**job)
    try:
        v.save()
    except DatabaseError:
        pass

# Запись полученных ошибок в БД
if errors:
    qs = Error.objects.filter(timestamp=datetime.date.today())
    if qs.exists():
        err = qs.first()
        err.data.update({'errors': errors})
        err.save()
    else:
        er = Error(data=f'errors: {errors}').save()
