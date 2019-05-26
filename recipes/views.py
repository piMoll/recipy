from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from .models import Tag, Recipe, Ingredient, Direction, Picture
from django.views.generic.detail import DetailView
from django.db.models import Q


def index(request):
    tags = Tag.objects.all()
    html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family:sans-serif;
                    font-weight:bold;
                }}
                ul {{
                    list-style-type:none;
                }}
                .tag {{
                    border-radius:5px;
                    display:inline-block;
                    margin:3px;
                    padding:4px 7px;
                }}
            </style>
        </head>
        <body>
            <h3>Available Tags ({len(tags)}):</h3>
            <ul>
                {''.join([f'<li class="tag" style="color:{t.font};background-color:{t.color}">{t.name}</li>' for t in tags])}
            </ul>
        </body>
    </html>
    """
    return HttpResponse(html)


class RecipeDetailsView(DetailView):
    model = Recipe


def search(request):
    if request.method == 'GET':
        query = request.GET.get('searchstring')
        submitbutton = request.GET.get('submit')

        if query is not None:
            lookups = Q(title__icontains=query)
            results = Recipe.objects.filter(lookups).distinct()
            context = {'results': results,
                       'submitbutton': submitbutton}
            return render(request, 'recipes/search.html', context)
        else:
            return render(request, 'recipes/search.html')
    else:
        return render(request, 'recipes/search.html')