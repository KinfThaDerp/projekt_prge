import requests
from bs4 import BeautifulSoup
header = {
        "User-Agent": "<Mozilla 5/0 (Windows NT 10.0; Win64; x64; Trident/7.0)>",
    }


def get_Coordinates(location:str) -> list[float]:
    url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url, headers=header)
    response_html = BeautifulSoup(response.content, 'html.parser')
    latitude = float((response_html.select('.latitude'))[1].text.replace(',', '.'))
    longitude = float((response_html.select('.longitude'))[1].text.replace(',', '.'))
    return [latitude, longitude]


def scrape_voivodeship(location) -> str | None:
    url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url, headers=header)
    response_html = BeautifulSoup(response.content, 'html.parser')

    links = response_html.find_all('a', title=True)
    for link in links:
        title = link['title']
        if title.startswith('Województwo '):
            return link.text.strip()
    return None