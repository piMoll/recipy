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
    def save(self, commit=True):
        """
        First, build a summary with the following structure:
        {
            "TEIG": [<Ingredient Mehl>, <Ingredient Milch>,],
        }
        Next, for each group, for each Ingredient, set the order.
        """
        groups = {}
        for form in self.ordered_forms:
            if not form.cleaned_data or self.can_delete and self._should_delete_form(form):
                continue
            if form.instance.group not in groups:
                groups[form.instance.group] = []
            groups[form.instance.group].append(form.instance)

        i = 0
        for group in groups.values():
            for instance in group:
                i += 1
                instance.order_item = i
        super().save(commit=commit)


IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient,
    fields=(
        'quantity',
        'name',
        'group',
        'order_item',
    ),
    extra=0,
    max_num=100,
    formset=IngredientOrderEnumerator,
    form=IngredientForm,
    can_order=True,
)


class DirectionForm(forms.ModelForm):
    step = forms.IntegerField(required=False)


class DirectionStepEnumerator(BaseInlineFormSet):
    def save(self, commit=True):
        i = 0
        for form in self.ordered_forms:
            if not form.cleaned_data or self.can_delete and self._should_delete_form(form):
                continue
            i += 1
            form.instance.step = i
        super().save(commit=commit)


DirectionFormSet = inlineformset_factory(
    Recipe, Direction,
    fields=(
        'step',
        'description',
    ),
    extra=0,
    max_num=20,
    labels={
        'description': 'Schritt'
    },
    formset=DirectionStepEnumerator,
    form=DirectionForm,
    can_order=True,
)
