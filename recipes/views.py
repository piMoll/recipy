from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View, ListView, RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .logger import logger
from .models import Tag, Recipe, Collection
from .forms import RecipeCreateForm, IngredientFormSet, DirectionFormSet, PictureFormSet, SearchForm
from .search import search_recipes
from .templatetags.recipes import recipe_vuemodel


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
    accept_json = True  # we're only making "rest"-style requests anyway

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
                logger.info('tried to POST recipe: %s', str(errors))
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
            logger.info('tried to GET recipe: %s', search_form.errors)
            response = {
                'success': False,
                'errors': search_form.errors,
            }
            status = {'status': 400}
        return JsonResponse(response, **status)


class CollectionShortDetailsView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Collection, **kwargs)
        return obj.get_absolute_url()


class CollectionDetailsView(LoginRequiredMixin, DetailView):
    model = Collection
    context_object_name = 'collection'


class CollectionDetailsPublicView(DetailView):
    model = Collection
    slug_field = 'public_slug'
    context_object_name = 'collection'


class CollectionOverviewView(LoginRequiredMixin, ListView):
    model = Collection


class CollectionEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('collection.change_collection', 'recipe.view_recipe')
    model = Collection
    fields = ('name', 'recipes')
    extra_context = {'tags': Tag.objects.order_by('id'),}

    def form_valid(self, form):
        accept_json = self.request.headers['Accept'] == 'application/json'
        if accept_json:
            self.object = form.save()
            return JsonResponse({
                'success': True,
                'location': self.get_success_url()
            })
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        logger.info('tried to POST collection: %s', form.errors)
        accept_json = self.request.headers['Accept'] == 'application/json'
        if accept_json:
            return JsonResponse({
                'errors': form.errors
            }, status=500)
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset=queryset)
        except AttributeError:
            return None
