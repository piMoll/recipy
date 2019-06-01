from django.shortcuts import get_object_or_404, render
from .models import Tag, Recipe, Ingredient, Direction, Picture
from django.views.generic.detail import DetailView


class RecipeDetailsView(DetailView):
    model = Recipe
    context_object_name = 'recipe'


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
        tag_key = f'tag.{tag.name}'
        params = get.copy()
        current_state = params.pop(tag_key, [None])[-1]  # it's a multi value dict, so it returns a list

        next_state = get_next_tag_state(current_state)
        if next_state:  # don't insert None values
            params[f'tag.{tag.name}'] = next_state

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

        query = Recipe.objects

        for tag in Tag.objects.all():
            if not request.GET.get(f'tag.{tag.name}', False):
                continue
            val = request.GET.get(f'tag.{tag.name}')
            if val == 'y':
                query = query.filter(tags=tag)
            elif val == 'n':
                query = query.exclude(tags=tag)

        search_string = request.GET.get('search_string')
        if search_string is not None:
            query = query.filter(title__icontains=search_string)

            context.update(
                search_string=search_string,
                search_results=query.distinct(),
            )

    return render(request, 'recipes/search.html', context=context)
