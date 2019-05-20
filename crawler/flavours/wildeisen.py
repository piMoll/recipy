import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from ..crawler import http_get, get_json, levenshtein, ImportException
from recipes.models import Recipe, Direction, Ingredient, Picture, Tag


class Wildeisen(object):
    SEARCH_URL = 'https://www.wildeisen.ch/suche/rezepte'
    RECIPE_URL = 'https://www.wildeisen.ch/rezepte'

    def __init__(self, crawler_input):
        self.input = crawler_input
        search_results = get_json(self.SEARCH_URL, params={'q': self.input})

        self.json = search_results['results'][0]

        slug = self.json['slug']
        raw = http_get(self.RECIPE_URL + f'/{slug}')

        self.dom = BeautifulSoup(raw, 'html.parser')

    def validate(self, name):
        input_len = len(self.input)
        distance = levenshtein(self.input, name[0:input_len])
        return 1 - (distance / input_len)

    def save(self):
        r = Recipe()

        r.title = self.find_title()
        r.preparationtime = self.find_preparationtime()
        r.cooktime = self.find_cooktime()
        r.resttime = self.find_resttime()
        r.portion_quantity = self.find_portion_quantity()
        r.portion_unit = self.find_portion_unit()
        r.nutrition_kcal = self.find_nutrition_kcal()
        r.nutrition_carbs = self.find_nutrition_carbs()
        r.nutrition_fat = self.find_nutrition_fat()
        r.nutrition_protein = self.find_nutrition_protein()
        r.note = self.find_note()
        r.author = self.find_author()
        r.source = self.find_source()

        r.save()

        self.add_ingredients(r.id)
        self.add_directions(r.id)
        self.add_pictures(r.id)
        r.tags.add(self.find_tags())

        return {
            'input': self.input,
            'found_recipe': r.title,
            'reliability': self.validate(r.title),
        }

    def find_title(self):
        return self.json['name']

    TIME_RE = re.compile(r'.*:\s*(\d+)')

    def find_preparationtime(self):
        texts = self.dom.select('[itemprop="prepTime"]')
        if len(texts) == 0:
            return None
        if len(texts) == 1:
            text = texts[0].string.strip()
            time = self.TIME_RE.match(text).group(1)
            return int(time)
        raise ImportException('Found too many [itemprop=prepTime] tags')

    def find_cooktime(self):
        texts = self.dom.select('[itemprop="cookTime"]')
        if len(texts) == 0:
            return None
        if len(texts) == 1:
            text = texts[0].string.strip()
            time = self.TIME_RE.match(text).group(1)
            return int(time)
        raise ImportException('Found too many [itemprop=cookTime] tags')

    def find_resttime(self):
        # note: no spaces between, all selectors target the same tag
        texts = self.dom.select('.media__sharing__time__item'
                                ':not([itemprop="cookTime"])'
                                ':not([itemprop="prepTime"])')
        if len(texts) == 0:
            return None
        if len(texts) == 1:
            text = texts[0].string.strip()
            time = self.TIME_RE.match(text).group(1)
            return int(time)
        raise ImportException('Found too many rest-time tags')

    YIELD_RE = re.compile(r'.*(\d+(?:-\d+)?)\s+(\w+)')

    def find_portion_quantity(self):
        texts = self.dom.select('[itemprop="recipeYield"]')
        if len(texts) == 1:
            text = texts[0].string.strip()
            qnt = self.YIELD_RE.match(text).group(1)
            return int(qnt)
        raise ImportException('Found !=1 [itemprop=recipeYield] tags')

    def find_portion_unit(self):
        texts = self.dom.select('[itemprop="recipeYield"]')

        if len(texts) != 1:
            raise ImportException('Found !=1 [itemprop=recipeYield] tags')

        text = texts[0].string.strip()
        unit = self.YIELD_RE.match(text).group(2).lower()

        try:
            return {
                'stück': Recipe.PIECES,
                'portionen': Recipe.PORTIONS,
                'portion': Recipe.PORTIONS,
                'personen': Recipe.PORTIONS,
            }[unit]
        except KeyError as ke:
            raise ImportException(f'Don\'t know how to interpret portion unit "{unit}"', ke)

    def find_nutrition_kcal(self):
        texts = self.dom.select('[itemprop="calories"] > span.is--bold')
        if len(texts) > 1:
            raise ImportException('Found too many [itemprop=calories] tag')
        if len(texts) == 0:
            return None
        text = texts[0].string
        return int(text)

    def find_nutrition_carbs(self):
        texts = self.dom.select('[itemprop="carbohydrateContent"] > span.is--bold')
        if len(texts) > 1:
            raise ImportException('Found too many [itemprop=carbohydrateContent] tag')
        if len(texts) == 0:
            return None
        text = texts[0].string[:-1]  # strip 'g' (from e.g. '20g')
        return int(text)

    def find_nutrition_fat(self):
        texts = self.dom.select('[itemprop="fatContent"] > span.is--bold')
        if len(texts) > 1:
            raise ImportException('Found too many [itemprop=fatContent] tag')
        if len(texts) == 0:
            return None
        text = texts[0].string[:-1]  # strip 'g' (from e.g. '20g')
        return int(text)

    def find_nutrition_protein(self):
        texts = self.dom.select('[itemprop="proteinContent"] > span.is--bold')
        if len(texts) > 1:
            raise ImportException('Found too many [itemprop=proteinContent] tag')
        if len(texts) == 0:
            return None
        text = texts[0].string[:-1]  # strip 'g' (from e.g. '20g')
        return int(text)

    def find_note(self):
        texts = self.dom.select('.aside__section--ingredients--hint')
        if len(texts) > 1:
            raise ImportException('Found too many notes')
        if len(texts) == 0:
            return ''
        return texts[0].get_text()

    def find_author(self):
        return ''

    def find_source(self):
        slug = self.json['slug']
        return self.RECIPE_URL + f'/{slug}'

    def add_ingredients(self, recipe_id):
        ingredients = []

        sections = self.dom.select('.ingredients__section')
        for i, section in enumerate(sections):
            group = section.select('.headline__xsmall__bold')
            if len(group) > 1:
                raise ImportException('Found too many group headlines')
            if len(group) == 1:
                group = group[0].string.strip()
                if group[-1] == ':':
                    group = group[:-1]
            else:
                group = ''

            items = section.select('[itemprop="recipeIngredient"]')
            for j, item in enumerate(items):
                contents = item.contents
                while isinstance(contents[0], NavigableString):
                    contents.pop(0)

                quantity = contents.pop(0).string.strip()

                rest = [tag.string or '' for tag in contents]  # get strings
                rest = [text.strip() for text in rest if text.strip()]  # remove empty strings
                name = ' '.join(rest)

                ingredient = Ingredient(
                    quantity=quantity,
                    name=name,
                    group=group,
                    order_group=i,
                    order_item=j,
                    recipe_id=recipe_id
                )
                ingredients.append(ingredient)

        Ingredient.objects.bulk_create(ingredients)

    def add_directions(self, recipe_id):
        Direction.objects.bulk_create([
            Direction(step=i + 1,
                      description=step['description'],
                      recipe_id=recipe_id)
            for i, step in enumerate(self.json['preparation_steps'])
        ])

    def add_pictures(self, recipe_id):
        pass

    def find_tags(self):
        return Tag.objects.get(name='unvollständig')
