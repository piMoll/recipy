from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Tag, Recipe, Ingredient, Direction
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from .forms import RecipeCreateForm, IngredientForm, DirectionForm, IngredientOrderEnumerator, DirectionStepEnumerator
from django.forms import inlineformset_factory, HiddenInput, TextInput
from recipy import settings


class RecipeDetailsView(DetailView):
    model = Recipe
    context_object_name = 'recipe'

class RecipeDetailsPublicView(DetailView):
    model = Recipe
    slug_field = 'public_slug'
    context_object_name = 'recipe'

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


class RecipeCreate(FormView):
    form_class = RecipeCreateForm
    template_name = 'recipes/recipe_create.html'
    success_url = '.'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return {
            'formset': inlineformset_factory(Recipe, Ingredient, fields=(
                'quantity', 'name'))
        }


def create(request, pk=None):
    recipe_form = None
    ingredient_formset = None
    direction_formset = None
    recipe = None

    if pk is not None:
        recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == "POST":
        recipe_form = RecipeCreateForm(data=request.POST, instance=recipe)
        if recipe_form.is_valid():
            recipe = recipe_form.save()

            ingredient_formset = IngredientFormSet(data=request.POST, instance=recipe)
            if ingredient_formset.is_valid():
                ingredients = ingredient_formset.save()

            direction_formset = DirectionFormSet(data=request.POST, instance=recipe)
            if direction_formset.is_valid():
                directions = direction_formset.save()

            if ingredient_formset.is_valid() and direction_formset.is_valid():
                return HttpResponseRedirect(reverse('recipes:detail', kwargs={'pk': recipe.pk}))

    elif request.method == 'GET':
        recipe_form = RecipeCreateForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)
        direction_formset = DirectionFormSet(instance=recipe)

    return render(request, 'recipes/recipe_create.html', {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'direction_formset': direction_formset,
        'tag_list': Tag.objects.all()
    })


def get_next_tag_state(state):
    return {
        None: 'y',
        'y': 'n',
        'n': None,
    }.get(state, 'y')


def get_next_tag_states(request):
    get = request.GET
    result = []
    reset_tags = None  # {key: value }

    # go over every tag that should be displayed
    for tag in Tag.objects.all():
        tag_key = tag.query_key()
        params = get.copy()
        current_state = params.pop(tag_key, [None])[-1]  # it's a multi value dict, so it returns a list

        next_state = get_next_tag_state(current_state)
        if next_state:  # don't insert None values
            params[tag_key] = next_state

        if current_state is not None:
            reset_tags = True

        query = params.urlencode()
        result.append((tag, query, current_state))

    if reset_tags:
        reset_tags = get.copy()
        for key in get:
            if key.startswith('tag.'):
                del reset_tags[key]
        reset_tags = reset_tags.urlencode()

    return result, reset_tags


def search(request):
    context = {}

    if request.method == 'GET':
        tag_list, reset_tags = get_next_tag_states(request)
        context.update(
            tag_list=tag_list,
            reset_tags=reset_tags
        )

        random_sample = Recipe.objects.order_by('?')[:6]

        query = Recipe.objects.all().distinct()
        query_ = query

        # TODO: optimize? //stackoverflow.com/a/8637972/4427997
        for tag in Tag.objects.all():
            # skip if the tag is None or ''. We don't care for multiple values, taking last is fine
            if not request.GET.get(f'tag.{tag.name}', False):
                continue

            # we already checked for no value
            val = request.GET[f'tag.{tag.name}']
            if val == 'y':
                query = query.filter(tags=tag)
            elif val == 'n':
                query = query.exclude(tags=tag)

        search_string = request.GET.get('search_string')
        if search_string:

            db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]
            if db_backend == 'postgresql':
                from django.contrib.postgres.aggregates import StringAgg
                from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

                searchV = SearchVector('title', weight='B') \
                          + SearchVector(StringAgg('ingredient__name', delimiter=' '), weight='C') \
                          + SearchVector(StringAgg('direction__description', delimiter=' '), weight='C')

                terms = [SearchQuery(term+':*', search_type='raw') for term in search_string.split()]
                searchQ = terms[0]
                for sq in terms[1:]:
                    searchQ &= sq

                query = query.annotate(
                    search=searchV,
                    rank=SearchRank(searchV, searchQ)
                    ).filter(search=searchQ).filter(rank__gt=0).order_by('-rank')

            else:
                query = query.filter(title__icontains=search_string)

            context.update(
                search_string=search_string,
            )

        result = random_sample if query is query_ else query

        context.update(
            search_results=result,
        )

    return render(request, 'recipes/search.html', context=context)
