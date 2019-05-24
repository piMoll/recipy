from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from .models import Tag, Recipe, Ingredient, Direction, Picture


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


def detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    picture = Picture.objects.filter(recipe=recipe_id)[0]
    tags = Tag.objects.filter(recipe=recipe_id)
    ingredients = Ingredient.objects.filter(recipe=recipe_id).order_by('order_item')
    directions = Direction.objects.filter(recipe=recipe_id).order_by('step')
    context = {
        'recipe': recipe,
        'picture': picture,
        'tags': tags,
        'ingredients': ingredients,
        'directions': directions
    }
    return render(request, 'recipes/index.html', context)
