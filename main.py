import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers

HOST = "https://spb.hh.ru/"
CONDITIONS = "/search/vacancy?text=python&area=1&area=2"
LINK = f'{HOST}{CONDITIONS}'

def get_headers():
    return Headers(browser="Google Chrome", os='win').generate()

def get_text(url):
    return requests.get(url, headers=get_headers()).text

list_links = []
target_list = []

def scraping_vacancy_links():
    soup = BeautifulSoup(get_text(LINK), 'lxml')
    vacancies = soup.find_all('a', class_="serp-item__title")
    for vacancy in vacancies:
        links = vacancy["href"]
        response_links = requests.get(links, headers=get_headers())
        links_parsed = BeautifulSoup(response_links.text, 'lxml')
        vacancy_description = links_parsed.find("div", {"data-qa": "vacancy-description"})
        if not vacancy_description:
            continue
        if ("Django" or "Flask") in vacancy_description.text:
            list_links.append(links)
    # print(list_links)

def scraping_vacancy():
    for l in list_links:
        link = requests.get(l, headers=get_headers())
        vacancy_scraping = BeautifulSoup(link.text, 'lxml')
        salary = vacancy_scraping.find("span", class_="bloko-header-section-2 bloko-header-section-2_lite")
        if "USD" not in salary:
            continue
        city = vacancy_scraping.find("p", {"data-qa": "vacancy-view-location"})
        if not city:
            continue
        company = vacancy_scraping.find("a", {"data-qa": "vacancy-company-name"})
        if not company:
            continue
        target_list.append(
            {
                "link": l,
                "salary": salary.text,
                "city": city.text,
                "company": company.text
            }
        )
    return target_list

if __name__ == "__main__":
    scraping_vacancy_links()
    scraping_vacancy()
    with open("vacancies_USD.json", "w", encoding="utf-8") as data:
        json.dump(target_list, data, indent=2, ensure_ascii=False)