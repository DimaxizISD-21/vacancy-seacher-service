import requests
from bs4 import BeautifulSoup
from random import randint

__all__ = ('work_ua_parser', 'rabota_ua_parser', 'dou_ua_parser', 'djinni_parser')

headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'},

    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 OPR/72.0.3815.320.',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'},

    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'},

    {'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'},
]


#---------------------------- Work.ua parser ----------------------------

def work_ua_parser(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://www.work.ua'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 3)])
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            main_div = soup.find('div', id='pjax-job-list')
            if main_div:
                div_list = main_div.find_all('div', attrs={'class': 'job-link'})
                for div in div_list:
                    title = div.find('h2')
                    href = title.a['href']
                    company = 'No name'
                    description = div.p.text
                    logo = div.find('img')
                    comp = div.find('span').b
                    if logo:
                        company = logo['alt']
                    elif comp:
                        company = comp.text

                    jobs.append({
                        'title': title.text.strip(),
                        'url': domain + href,
                        'company': company,
                        'description': description,
                        'city_id': city,
                        'language_id': language,
                    })
            else:
                errors.append({
                    'url': url,
                    'title': "Div does not exists",
                })

        else:
            errors.append({
                'url': url,
                'title': "Page do not response",
            })

    return jobs, errors

#---------------------------- Rabota.ua parser ----------------------------

def rabota_ua_parser(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://rabota.ua'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 3)])
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            new_jobs = soup.find('div', attrs={"class": 'f-vacancylist-newnotfound'})
            if not new_jobs:
                table = soup.find('table', id='ctl00_content_vacancyList_gridList')
                if table:
                    tr_list = table.find_all('tr', attrs={'id': True})
                    for tr in tr_list:
                        div = tr.find('div', attrs={'class': 'card-body'})
                        if div:
                            title = div.find('h2', attrs={'class': 'card-title'})
                            href = title.a['href']
                            company = 'No name'
                            p = div.find('p', attrs={'class': 'company-name'})
                            if p:
                                company = p.a.text

                            description = div.find('div', attrs={'class': 'card-description'})

                            jobs.append({
                                'title': title.text.strip(),
                                'url': domain + href,
                                'company': company,
                                'description': description.text.strip(),
                                'city_id': city,
                                'language_id': language,
                            })
                else:
                    errors.append({
                        'url': url,
                        'title': "Table does not exists",
                    })

            else:
                errors.append({
                    'url': url,
                    'title': "Page is empty",
                })

        else:
            errors.append({
                'url': url,
                'title': "Page do not response",
            })

    return jobs, errors

#---------------------------- Dou.ua parser ----------------------------

def dou_ua_parser(url, city=None, language=None):
    jobs = []
    errors = []
    if url:
        resp = requests.get(url, headers=headers[randint(0, 3)])
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            main_div = soup.find('div', id='vacancyListId')
            if main_div:
                div_list = main_div.find_all('div', attrs={'class': 'vacancy'})
                for div in div_list:
                    title = div.find('div', attrs={'class': 'title'})
                    href = title.a['href']
                    company = 'No name'
                    a = div.find('a', attrs={'class': 'company'})
                    if a:
                        company = a.text

                    description = div.find('div', attrs={'class': 'sh-info'}).text.strip()

                    jobs.append({
                        'title': title.a.text,
                        'url': href,
                        'company': company,
                        'description': description,
                        'city_id': city,
                        'language_id': language,
                    })
            else:
                errors.append({
                    'url': url,
                    'title': "Div does not exists",
                })

        else:
            errors.append({
                'url': url,
                'title': "Page do not response",
            })

    return jobs, errors

#---------------------------- Djinni parser ----------------------------

def djinni_parser(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://djinni.co'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 3)])
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            main_ul = soup.find('ul', attrs={'class': 'list-jobs'})
            if main_ul:
                li_list = main_ul.find_all('li', attrs={'class': 'list-jobs__item'})
                for li in li_list:
                    title = li.find('div', attrs={'class': 'list-jobs__title'})
                    href = title.a['href']
                    company = 'No name'
                    comp = li.find('div', attrs={'class': 'list-jobs__details__info'}).text
                    if comp:
                        company = comp
                    description = 'No have description'
                    descr = li.find('div', attrs={'class': 'list-jobs__description'}).p.text
                    if descr:
                        description = descr

                    jobs.append({
                        'title': title.text.strip(),
                        'url': domain + href,
                        'company': company,
                        'description': description,
                        'city_id': city,
                        'language_id': language,
                    })
            else:
                errors.append({
                    'url': url,
                    'title': "Div does not exists",
                })

        else:
            errors.append({
                'url': url,
                'title': "Page do not response",
            })

    return jobs, errors
