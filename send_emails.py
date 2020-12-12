import os, sys
import django
import datetime
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

# Делаем send_emails видимым для Django
project = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project)
os.environ['DJANGO_SETTINGS_MODULE'] = "vacancy_seacher.settings"

django.setup()
from scraping.models import Vacancy, Error, Url
from vacancy_seacher.settings import EMAIL_HOST_USER

ADMIN_USER = EMAIL_HOST_USER

# Формирование данных для сообщения
today = datetime.date.today()
empty = '<h2>К сожалению на сегодня по Вашим предпочтениям данных нет.</h2>'
subject = f'Рассылка вакансий за {today}'
text_content = f'Рассылка вакансий {today}'
from_email = EMAIL_HOST_USER

# Импортируем пользователя, который подписан на рассылку
User = get_user_model()
qs = User.objects.filter(send_email=True).values('city', 'language', 'email')
users_dict = {}

# Перебираем данные пользователя
for i in qs:
    users_dict.setdefault((i['city'], i['language']), [])
    users_dict[(i['city'], i['language'])].append(i['email'])

# Перебираем пары (Город/Язык програмирования) конкретного пользователя
if users_dict:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in users_dict.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])

    # Выбираем свежие добавленые вакансии за сегодня
    # и отправляем их пользователям, которые подписаны на рассылку
    qs = Vacancy.objects.filter(**params, timestamp=today).values()
    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)
        for keys, emails in users_dict.items():
            rows = vacancies.get(keys, [])
            html = ''
            for row in rows:
                html += f'<h5><a href="{row["url"]}">{row["title"]}</a></h5>'
                html += f'<p>{row["description"]}</p>'
                html += f'<p>{row["company"]}</p><br><hr>'
            _html = html if html else empty
            for email in emails:
                to = email
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(_html, "text/html")
                msg.send()

# Отправка ошибок парсинга администратору сервиса
qs = Error.objects.filter(timestamp=today)
subject = ''
text_content = ''
to = ADMIN_USER
_html = ''

if qs.exists():
    error = qs.first()
    data = error.data.get('errors', [])
    for i in data:
        _html += f'<p><a href="{ i["url"] }">Error: { i["title"] }</a></p><br>'
    subject = f'Ошибки парсинга {today}'
    text_content = 'Ошибки парсинга'

    data = error.data.get('user_data')
    if data:
        _html += '<hr>'
        _html += '<h2>Пожелания пользователей</h2>'
        for i in data:
            _html += f'<p>Город: {i["city"]}, Язык програмирования: {i["language"]}, Email: {i["email"]}</p><br>'
        subject = f'Пожелания пользователей {today}'
        text_content = 'Пожелания пользователей'

# Делаем уведомления для адмминистратора сервиса, для какой пары (Город/Язык програмирования)
# у нас отстутсвуют соотвествующи urls
qs = Url.objects.all().values('city', 'language')
urls_dict = {(i['city'], i['language']): True for i in qs}
urls_errors = ''
for keys in users_dict.keys():
    if keys not in urls_dict:
        if keys[0] and keys[1]:
            urls_errors += f'<p>Для города { keys[0] } и языка програмирования { keys[1] } отсутствуют ссылка для парсинга!</p><br>'

if urls_errors:
    subject += ' Отсутствующие urls'
    _html += urls_errors

if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()
