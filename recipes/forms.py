from django import forms
from django.forms import CheckboxSelectMultiple, BaseInlineFormSet

from .models import Recipe, Ingredient, Direction, Picture, Tag


class TagSelectWidget(CheckboxSelectMultiple):
    option_template_name = 'recipes/recipes_create_tag.html'

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        option.update(
            model=Tag.objects.get(pk=option['value']),
        )
        return option


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
        widgets = {
            'tags': TagSelectWidget
        }


class IngredientForm(forms.ModelForm):
    order_item = forms.IntegerField(required=False)


class DirectionForm(forms.ModelForm):
    step = forms.IntegerField(required=False)


class IngredientOrderEnumerator(BaseInlineFormSet):
    def clean(self):
        super().clean()
        groups = {}
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data['DELETE']:
                continue
            if form.instance.group not in groups:
                groups[form.instance.group] = []
            groups[form.instance.group].append(form.instance)
        i = 0
        for group in groups:
            for instance in groups[group]:
                i += 1
                instance.order_item = i


class DirectionStepEnumerator(BaseInlineFormSet):
    def clean(self):
        super().clean()
        i = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data['DELETE']:
                continue
            i += 1
            form.instance.step = i