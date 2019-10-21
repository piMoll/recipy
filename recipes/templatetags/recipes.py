from django import template
from django.conf import settings

from ..models import format_duration


register = template.Library()


@register.filter
def get_setting(name):
    return getattr(settings, name, "")


@register.filter
def hours_minutes(number):
    return format_duration(number)


@register.filter
def order_by(queryset, field):
    return queryset.order_by(field)


@register.filter
def recipe_thumbnail(recipe):
    return recipe.picture_set.order_by('order').first().thumbnail.url


def prepare_for_vue(recipe):
    """
    :type recipe: recipes.models.Recipe
    """
    return {
        'id': recipe.id,
        'title': recipe.title,
        'thumbnail': recipe_thumbnail(recipe),
        'url': recipe.get_absolute_url(),
        'tags': list(recipe.tags_sorted().values('color', 'font', 'name'))
    }


@register.filter
def make_real_list(iterable):
    return list(iterable)


@register.filter
def attr(dictionary, key):
    return dictionary[key]


@register.filter
def recipe_vuemodel(recipes):
    recipes = recipes.prefetch_related('picture_set', 'tags')
    return [prepare_for_vue(recipe) for recipe in recipes]
