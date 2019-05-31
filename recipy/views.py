from django.views.generic import RedirectView


class StartPage(RedirectView):
    pattern_name = 'recipes:search'
