from django import forms
from django.forms import CheckboxSelectMultiple, BaseInlineFormSet, inlineformset_factory, TextInput, HiddenInput, ImageField

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
    # tags = forms.ModelChoiceField(queryset=Tag.objects.all(), required=False)
    picture = ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'title',
            'picture',
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
            'note',
        )
        widgets = {
            'tags': TagSelectWidget
        }


class IngredientForm(forms.ModelForm):
    order_item = forms.IntegerField(required=False)


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


IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient,
    fields=(
        'quantity',
        'name',
        'group',
        'order_item',
    ),
    extra=15,
    formset=IngredientOrderEnumerator,
    widgets={
        'quantity': TextInput(),
        'name': TextInput(),
        'order_item': HiddenInput(),
        'group': HiddenInput(),
        'DELETE': HiddenInput(),
    },
    form=IngredientForm,
)


class DirectionForm(forms.ModelForm):
    step = forms.IntegerField(required=False)


class DirectionStepEnumerator(BaseInlineFormSet):
    def clean(self):
        super().clean()
        i = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data['DELETE']:
                continue
            i += 1
            form.instance.step = i


DirectionFormSet = inlineformset_factory(
    Recipe, Direction,
    fields=(
        'step',
        'description',
    ),
    extra=7,
    labels={
        'description': 'Schritt'
    },
    widgets={
        'step': HiddenInput(),
    },
    formset=DirectionStepEnumerator,
    form=DirectionForm,
)
