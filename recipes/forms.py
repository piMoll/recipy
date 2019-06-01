from django import forms
from .models import Recipe, Ingredient, Direction, Picture


class RecipeCreateForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = [
            'title',
            'preparationtime',
            'cooktime',
            'resttime',
            'portion_quantity',
            'portion_unit',
            'nutrition_kcal',
            'nutrition_carbs',
            'nutrition_fat',
            'nutrition_protein',
            'tags',
            'source',
            # 'ingredients',
            # 'directions',
            'note',
        ]
