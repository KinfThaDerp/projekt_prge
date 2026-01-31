import requests
from bs4 import BeautifulSoup
header = {"User-Agent": "<Mozilla 5/0 (Windows NT 10.0; Win64; x64; Trident/7.0)>",}

import requests
from bs4 import BeautifulSoup



def scrape_coordinates(location: str) -> dict:
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=xml&limit=1"
    try:
        response = requests.get(url, headers=header, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        place = soup.find('place')

        if place:
            lat = place.get('lat')
            lon = place.get('lon')
            return {
                "lat": float(lat) if lat else None,
                "lon": float(lon) if lon else None,
                "success": True
            }

        return {"error": "No results found", "success": False}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}", "success": False}


def scrape_voivodeship(location) -> str | None:
    try:
        url: str = f'https://pl.wikipedia.org/wiki/{location}'
        response = requests.get(url, headers=header)
        response_html = BeautifulSoup(response.content, 'html.parser')

        links = response_html.find_all('a', title=True)
        for link in links:
            title = link['title']
            if title.startswith('Województwo '):
                return link.text.strip()
        raise ValueError(f"Could not find voivodeship")
    except Exception as e:
        print({f"Scraping error for {location}: {str(e)}"})


if __name__ == '__main__':
    print(scrape_coordinates("Legionowo"))