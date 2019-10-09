from django import template
from django.conf import settings

from recipes.models import format_duration

register = template.Library()


@register.simple_tag
def get_setting(name):
    return getattr(settings, name, "")


@register.filter
def hours_minutes(number):
    return format_duration(number)


@register.filter
def order_by(queryset, field):
    return queryset.order_by(field)
