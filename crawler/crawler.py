from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from urllib.parse import quote as urlencode


def simple_get(url):
    def is_okay(response):
        content_type = response.headers['Content-Type'].lower()
        return response.status_code == 200

    try:
        with closing(get(url, stream=True)) as resp:
            if is_okay(resp):
                return resp.content
            else:
                return None
    except RequestException:
        return None


def find_recipe(recipe_title):
    def wildeisen_search(title):
        return 'https://www.wildeisen.ch/suche/rezepte?q=' + urlencode(title)

    return simple_get(wildeisen_search(recipe_title))
    raw = simple_get(wildeisen_search(recipe_title))
    dom = BeautifulSoup(raw, 'html.parser')
    li = dom.select('.teaser-list__item')[0]
    a = li.select('a[itemprop="url"]')[0]
    return a.href

def import_recipe(recipe_title):
    url = find_recipe(recipe_title)
    raw = simple_get('https://www.wildeisen.ch' + url)
    dom = BeautifulSoup(raw, 'html.parser')
    return raw







