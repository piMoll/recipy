from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, RedirectView, TemplateView
from django.views.generic.detail import DetailView

from .models import Tag, Recipe, Collection
from .forms import RecipeCreateForm, IngredientFormSet, DirectionFormSet, PictureFormSet, SearchForm
from .templatetags.recipes import recipe_vuemodel
from recipy import settings


class RecipeShortDetailsView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Recipe, **kwargs)
        return obj.get_absolute_url()


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
    picture_formset = None
    ingredient_formset = None
    direction_formset = None
    recipe = None  # type: Recipe or None
    close_url = reverse('recipes:search')
    accept_json = request.headers['Accept'] == 'application/json'

    if pk is not None:
        recipe = get_object_or_404(Recipe, pk=pk)
        close_url = recipe.get_absolute_url()

    if recipe is None and not request.user.has_perm('recipes.add_recipe') or \
            recipe is not None and not request.user.has_perm('recipes.change_recipe'):
        raise PermissionDenied

    if request.method == "POST":
        # recipe_form.save() must be called before initializing IngredientFormSet and DirectionFormSet, so we can set
        # the instance properly. Additionally, both FormSets must be initialized so we can keep the entered data in
        # case of an error. However, if there is an error somewhere, we need to rollback the recipe_form.save().
        # We do so by using `with transaction.atomic():`, and breaking out by means of `raise`.
        try:
            with transaction.atomic():
                no_errors = True

                recipe_form = RecipeCreateForm(data=request.POST, files=request.FILES, instance=recipe)
                no_errors = no_errors and recipe_form.is_valid()
                if no_errors:
                    recipe = recipe_form.save()

                picture_formset = PictureFormSet(data=request.POST, files=request.FILES, instance=recipe)
                no_errors = no_errors and picture_formset.is_valid()

                ingredient_formset = IngredientFormSet(data=request.POST, instance=recipe)
                no_errors = no_errors and ingredient_formset.is_valid()

                direction_formset = DirectionFormSet(data=request.POST, instance=recipe)
                no_errors = no_errors and direction_formset.is_valid()

                if no_errors:
                    picture_formset.save()
                    ingredient_formset.save()
                    direction_formset.save()
                else:
                    raise RuntimeError

                if accept_json:
                    return JsonResponse({
                        'success': True,
                        'location': recipe.get_absolute_url()
                    })
                else:
                    return HttpResponseRedirect(recipe.get_absolute_url())

        except RuntimeError:
            if accept_json:
                forms = {
                    'recipe_form': recipe_form,
                    'picture_formset': picture_formset,
                    'ingredient_formset': ingredient_formset,
                    'direction_formset': direction_formset,
                }
                errors = {name: form.errors for name, form in forms.items() if not form.is_valid()}
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                })

    elif request.method == 'GET':
        recipe_form = RecipeCreateForm(instance=recipe)
        picture_formset = PictureFormSet(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)
        direction_formset = DirectionFormSet(instance=recipe)

    return render(request, 'recipes/recipe_create.html', {
        'recipe_form': recipe_form,
        'picture_formset': picture_formset,
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
    for tag in Tag.objects.all().order_by('pk'):
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


def search_recipes(search_string=None, tags=None):
    query = Recipe.objects.all().distinct()

    # TODO: optimize? //stackoverflow.com/a/8637972/4427997
    if tags:
        for tag in Tag.objects.all():
            if tags.get(tag.name, None) is None:  # value could be set to None, or not be set at all
                continue

            if tags[tag.name]:
                query = query.filter(tags=tag)
            else:
                query = query.exclude(tags=tag)

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

    return query


class SearchPageView(LoginRequiredMixin, TemplateView):
    template_name = 'recipes/search.html'
    random_choices = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = SearchForm(self.request.GET)
        if search_params.is_valid() and search_params.search_params:
            recipes = search_recipes(**search_params.search_params)
        else:
            recipes = Recipe.objects.order_by('?')[:self.random_choices]
        context['recipes'] = recipes
        context['search_form'] = search_params
        return context


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        search_form = SearchForm(request.GET)
        if search_form.is_valid() and search_form.search_params:
            recipes = search_recipes(**search_form.search_params)
            response = {
                'success': True,
                'recipes': recipe_vuemodel(recipes),
            }
            status = {}
        else:
            response = {
                'success': False,
                'errors': search_form.errors,
            }
            status = {'status': 400}
        return JsonResponse(response, **status)


class CollectionDetailsView(LoginRequiredMixin, DetailView):
    model = Collection
    context_object_name = 'collection'


class CollectionOverviewView(LoginRequiredMixin, ListView):
    model = Collection
