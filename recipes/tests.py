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
        
        self.recipeTomatensuppe.save() 
        self.recipePizza.save()
        self.recipeTomMozz.save()
        self.recipeBoerek.save()
        
        # Incridients
        Ingredient(recipe=self.recipeTomatensuppe, name='Knoblauch', order_item=0).save()
        Ingredient(recipe=self.recipePizza, name='Zwiebeln', order_item=0).save()
        Ingredient(recipe=self.recipeTomMozz, name='Zwiebeln', order_item=0).save()
        Ingredient(recipe=self.recipeBoerek, name='Feta', order_item=0).save()
        
        # Direction
        Direction(recipe=self.recipePizza, description='Küche auf den Kopf stellen', step=0).save()
    
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
        recipes: QuerySet[Recipe] = search_recipes('in')
        self.assertListEqual(list(recipes), [])
        recipes: QuerySet[Recipe] = search_recipes('vor')
        self.assertListEqual(list(recipes), [])
        recipes: QuerySet[Recipe] = search_recipes('der')
        self.assertListEqual(list(recipes), [])
    
