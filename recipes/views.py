from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView

from .models import Tag, Recipe, Picture
from .forms import RecipeCreateForm, IngredientFormSet, DirectionFormSet
from recipy import settings


class RecipeDetailsView(LoginRequiredMixin, DetailView):
    model = Recipe
    context_object_name = 'recipe'


class RecipeDetailsPublicView(DetailView):
    model = Recipe
    slug_field = 'public_slug'
    context_object_name = 'recipe'


@login_required
def create(request, pk=None):
    recipe_form = None
    ingredient_formset = None
    direction_formset = None
    recipe = None
    close_url = reverse('recipes:search')

    if pk is not None:
        recipe = get_object_or_404(Recipe, pk=pk)
        close_url = recipe.get_absolute_url()

    if request.method == "POST":
        # recipe_form.save() must be called before initializing IngredientFormSet and DirectionFormSet, so we can set
        # the instance properly. Additionally, both FormSets must be initialized so we can keep the entered data in
        # case of an error. However, if there is an error somewhere, we need to rollback the recipe_form.save().
        try:
            with transaction.atomic():
                no_errors = True

                recipe_form = RecipeCreateForm(data=request.POST, files=request.FILES, instance=recipe)
                no_errors = no_errors and recipe_form.is_valid()
                if no_errors:
                    recipe = recipe_form.save()

                    image = recipe_form.cleaned_data['picture']
                    if image:
                        # todo: add picture instead of replace
                        if recipe.picture_set.exists():
                            recipe.picture_set.get().delete()

                        new_picture = Picture(
                            recipe=recipe,
                            image=image,
                            order=0,
                            description=''
                        )
                        new_picture.save()

                ingredient_formset = IngredientFormSet(data=request.POST, instance=recipe)
                no_errors = no_errors and ingredient_formset.is_valid()
                if no_errors:
                    ingredient_formset.save()

                direction_formset = DirectionFormSet(data=request.POST, instance=recipe)
                no_errors = no_errors and direction_formset.is_valid()
                if no_errors:
                    direction_formset.save()

                if no_errors:
                    return HttpResponseRedirect(reverse('recipes:detail', kwargs={'pk': recipe.pk}))
                else:
                    raise RuntimeError()

        except RuntimeError:
            pass  # we just need to break the __open__()

    elif request.method == 'GET':
        recipe_form = RecipeCreateForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)
        direction_formset = DirectionFormSet(instance=recipe)

    return render(request, 'recipes/recipe_create.html', {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'direction_formset': direction_formset,
        'tag_list': Tag.objects.all(),
        'close_url': close_url
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

@login_required
def search(request):
    context = {}

    if request.method == 'GET':
        tag_list, reset_tags = get_next_tag_states(request)
        context.update(
            tag_list=tag_list,
            reset_tags=reset_tags
        )

        random_sample_count = 6
        random_sample = Recipe.objects.order_by('?')[:random_sample_count]

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

                search_v = SearchVector('title', weight='B') \
                    + SearchVector(StringAgg('ingredient__name', delimiter=' '), weight='C') \
                    + SearchVector(StringAgg('direction__description', delimiter=' '), weight='C')

                terms = [SearchQuery(term + ':*', search_type='raw') for term in search_string.split()]
                search_q = terms[0]
                for sq in terms[1:]:
                    search_q &= sq

                query = query.annotate(
                    search=search_v,
                    rank=SearchRank(search_v, search_q)
                ).filter(search=search_q).filter(rank__gt=0).order_by('-rank')

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
