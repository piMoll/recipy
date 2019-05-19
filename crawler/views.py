from django.http import HttpResponse, JsonResponse
from .flavours import available_flavours
from .crawler import Handler


def index(request):
    # these will be passed as parameters
    titles = [
        'spaghetti carbonara',
        'holunderblüten fizz',
        'knusper truffes',
    ]
    flavour = 'wildeisen'

    handler = available_flavours[flavour]['handler']  # type: type(Handler)

    imported_recipes = {}
    for title in titles:
        try:
            imported_recipes[title] = {
                'success': True,
                'result': handler(title).save()
            }
        except Exception as e:
            imported_recipes[title] = {
                'success': False,
                'result': e.args
            }

    return JsonResponse({
        'success': any((imp['success'] for imp in imported_recipes.values())),
        'data': imported_recipes
    })
