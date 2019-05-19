from bs4 import BeautifulSoup
from ..crawler import Handler
from recipes.models import Recipe, Direction, Ingredient, Picture, Tag


class Wildeisen(Handler):
    SEARCH_URL = 'https://www.wildeisen.ch/suche/rezepte'
    RECIPE_URL = 'https://www.wildeisen.ch/rezepte'

    def __init__(self, crawler_input):
        super().__init__(crawler_input)
        search_results = self.get_json(self.SEARCH_URL, params={'q': self.input})
        first_result = search_results['results'][0]
        self.reliability = self.validate(first_result['name'])
        slug = first_result['slug']
        raw = self.http_get(self.RECIPE_URL + f'/{slug}')
        self.dom = BeautifulSoup(raw, 'html.parser')

    def validate(self, name):
        input_len = len(self.input)
        distance = self.levenshtein(self.input, name[0:input_len])
        return 1 - (distance / input_len)

    def save(self):
        r = Recipe()

        r.title = self.find_title()
        r.preparationtime = self.find_preparationtime()
        r.cooktime = self.find_cooktime()
        r.portion_quantity = self.find_portion_quantity()
        r.portion_unit = self.find_portion_unit()
        r.nutrition_kcal = self.find_nutrition_kcal()
        r.nutrition_carbs = self.find_nutrition_carbs()
        r.nutrition_fat = self.find_nutrition_fat()
        r.nutrition_protein = self.find_nutrition_protein()
        r.note = self.find_note()
        r.author = self.find_author()
        r.source = self.find_source()
        r.creationdate = self.find_creationdate()
        r.tags = self.find_tags()

        r.save()

        r.ingredient_set.add(self.find_ingredients())
        r.direction_set.add(self.find_directions())
        r.picture_set.add(self.find_pictures())

        return {
            'input': self.input,
            'found_recipe': r.title,
            'reliability': self.validate(r.title),
        }

