from django import forms
from django.forms import CheckboxSelectMultiple, BaseInlineFormSet, inlineformset_factory, ImageField, Textarea

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
        fields = (
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
            'note',
            'author',
        )
        widgets = {
            'tags': TagSelectWidget,
            'note': Textarea,
        }


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
    can_order=True,
)


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
    can_order=True,
)


class PictureForm(forms.ModelForm):
    image = ImageField(required=False)


PictureFormSet = inlineformset_factory(
    Recipe, Picture,
    fields=(
        'image',
        'order',
        'description',
    ),
    extra=0,
    max_num=10,
    can_order=True,
    form=PictureForm,
)


class SearchForm(forms.Form):
    search_string = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = Tag.objects.order_by('pk')
        self.fields.update({
            f'tag.{tag.name}': forms.NullBooleanField(required=False) for tag in self.tags
        })
        self.search_params = {}

    def is_valid(self):
        valid = super().is_valid()
        fields = dict(self.cleaned_data)
        search_params = {}

        search_string = fields.pop('search_string')
        if search_string:
            search_params['search_string'] = search_string

        tags = {
            tag.split('.')[-1]: instruction
            for tag, instruction in fields.items()  # search_string was popped, only tags should remain
            if instruction is not None
        }
        if tags:
            search_params['tags'] = tags

        self.search_params = search_params
        return valid
