'''
Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта (также вводим
через input или аргументы). Получившийся список должен содержать в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью
dataFrame через pandas. Сохраните в json либо csv.
'''

from bs4 import BeautifulSoup as bs
import requests
import pandas


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

URL_FIRST_PAGE_HH = 'https://kazan.hh.ru/search/vacancy?area=88&search_field=name&search_field=company_name&search_field=description&text=python&no_magic=true&L_save_area=true&items_on_page=20&customDomain=1'

headers = {
    'User-Agent': USER_AGENT,
}


def parse_hh(url_page, headers, result=[], index_page=1):
    response = requests.get(url_page, headers=headers)
    if response.status_code != 200:
        return result

    dom = bs(response.content, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item__layout'})
    for vacancy in vacancies:
        result.append(parse_vacancy_hh(vacancy))

    link_next_page = dom.find('a', {'data-qa': 'pager-next'})
    if link_next_page:
        link_next_page = 'https://kazan.hh.ru' + link_next_page['href']
    else:
        return result

    result = parse_hh(link_next_page, headers, result, index_page + 1)
    return result


def parse_vacancy_hh(dom_vacancy):
    vacancy_name = dom_vacancy.find('a').text

    vacancy_salary = dom_vacancy.find('span', {'class', 'bloko-header-section-3'})
    if vacancy_salary:
        vacancy_salary = vacancy_salary.text
        min_salary, max_salary, currency_salary = clean_salary(vacancy_salary)
    else:
        min_salary, max_salary, currency_salary = None, None, None

    vacancy_link = dom_vacancy.find('a')['href']

    return {
        'vacancy_name': vacancy_name,
        'vacancy_salary': vacancy_salary,
        'min_salary': min_salary,
        'max_salary': max_salary,
        'currency_salary': currency_salary,
        'vacancy_link': vacancy_link,
        'vacancy_source': 'hh.ru',
    }


def clean_salary(vacancy_salary_text, min_salary=None, max_salary=None, currency_salary=None):
    list_salary = vacancy_salary_text.replace('\u202f', '').split()
    for i in range(len(list_salary) - 1):
        if list_salary[i] == 'от':
            min_salary = int(list_salary[i + 1])
        elif list_salary[i] == 'до':
            max_salary = int(list_salary[i + 1])
        elif list_salary[i] == '–':
            min_salary = int(list_salary[i - 1])
            max_salary = int(list_salary[i + 1])
    currency_salary = list_salary[-1]

    return min_salary, max_salary, currency_salary


result = parse_hh(URL_FIRST_PAGE_HH, headers)
print(pandas.DataFrame(result))
