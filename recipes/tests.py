from django.db.models import QuerySet
from django.test import TestCase

from recipes.models import Recipe, Ingredient, Direction
from recipes.search import search_recipes



class SearchTestCase(TestCase):
    
    def setUp(self):
        self.recipeTomatensuppe = Recipe(title='Tomatensuppe', portion_quantity=3)
        self.recipePizza = Recipe(title='Pizza', portion_quantity=4)
        self.recipeTomMozz = Recipe(title='TomMozzSalat', portion_quantity=4)
        self.recipeBoerek = Recipe(title='Börek', portion_quantity=4)
        self.recipeGurkenSalat = Recipe(title='Gurkensalat', portion_quantity=4)
        
        self.recipeTomatensuppe.save() 
        self.recipePizza.save()
        self.recipeTomMozz.save()
        self.recipeBoerek.save()
        self.recipeGurkenSalat.save()
        
        # Incidents
        Ingredient(recipe=self.recipeTomatensuppe, name='Knoblauch', order_item=0).save()
        Ingredient(recipe=self.recipePizza, name='Zwiebeln', order_item=0).save()
        Ingredient(recipe=self.recipePizza, name='Suppenhuhn', order_item=1).save()
        Ingredient(recipe=self.recipeTomMozz, name='Zwiebeln', order_item=0).save()
        Ingredient(recipe=self.recipeBoerek, name='Feta', order_item=0).save()
        
        # Direction
        Direction(recipe=self.recipeTomatensuppe, description='Suppe zubereiten, aber langsam', step=0).save()
        Direction(recipe=self.recipeTomatensuppe, description='Suppe köchern lassen, ganz langsam', step=1).save()
        Direction(recipe=self.recipePizza, description='Küche auf den Kopf stellen', step=0).save()
        Direction(recipe=self.recipeTomMozz, description='Vor das Haus gehen und das Walholz langsam begraben', step=0).save()
        Direction(recipe=self.recipeBoerek, description='Die Spinat suppe zubereiten, keine Cervala machen', step=0).save()
        Direction(recipe=self.recipeBoerek, description='Am besten keine Gurke nehmen', step=1).save()
    
    def testFindInTitle(self):
        recipes: QuerySet[Recipe] = search_recipes('Tomatensuppe')
        self.assertListEqual(list(recipes), [self.recipeTomatensuppe])
        
    def testFindPartialPrefixInTitle(self):
        recipes: QuerySet[Recipe] = search_recipes('Tom')
        self.assertListEqual(list(recipes), [self.recipeTomatensuppe, self.recipeTomMozz])
    
    def testFindInIngredient(self):
        recipes: QuerySet[Recipe] = search_recipes('Knoblauch')
        self.assertListEqual(list(recipes), [self.recipeTomatensuppe])
    
    def testFindInDirection(self):
        recipes: QuerySet[Recipe] = search_recipes('Kopf')
        self.assertListEqual(list(recipes), [self.recipePizza])
        
    def testFindWithUmlaut(self):
        recipes: QuerySet[Recipe] = search_recipes('Börek')
        self.assertListEqual(list(recipes), [self.recipeBoerek])
        
    def testIgnoreFillerWords(self):
        recipes: QuerySet[Recipe] = search_recipes('auf')
        self.assertListEqual(list(recipes), [])
        recipes: QuerySet[Recipe] = search_recipes('den')
        self.assertListEqual(list(recipes), [])
        recipes: QuerySet[Recipe] = search_recipes('vor')
        self.assertListEqual(list(recipes), [])
        recipes: QuerySet[Recipe] = search_recipes('das')
        self.assertListEqual(list(recipes), [])
    
    def testFindPostfixInTitle(self):
        search_string = 'salat'
        recipes: QuerySet[Recipe] = search_recipes(search_string)
        self.assertListEqual(list(recipes), [self.recipeTomMozz, self.recipeGurkenSalat])
        
    def testFindTermInTitleAsPostfixAndAsWholeWordsInOtherPlaces(self):
        search_string = 'suppe'
        recipes: QuerySet[Recipe] = search_recipes(search_string)
        self.assertEqual(len(list(recipes)), len([self.recipeTomatensuppe, self.recipePizza, self.recipeBoerek]))
        self.assertListEqual(list(recipes), [self.recipeTomatensuppe, self.recipePizza, self.recipeBoerek])

    def testHigherRankWithMoreMentions(self):
        search_string = 'langsam'
        recipes: QuerySet[Recipe] = search_recipes(search_string)
        self.assertListEqual(list(recipes), [self.recipeTomatensuppe, self.recipeTomMozz])
        

