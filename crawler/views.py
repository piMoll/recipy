from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .flavours import available_flavours
import json
import logging


def index(request):
    return HttpResponse(render(request, 'crawler/standalone.html'))


def batch(request):
    post = json.loads(request.body.decode('utf-8'))
    titles = post['titles'].strip().split('\n')
    flavour = post['flavour']

    handler = available_flavours[flavour]['handler']

    imported_recipes = {}
    for title in titles:
        try:
            imported_recipes[title] = {
                'success': True,
                'result': handler(title).save()
            }
        except Exception as e:
            logging.exception(e)
            imported_recipes[title] = {
                'success': False,
                'result': str(e)
            }

    return JsonResponse({
        'success': any((imp['success'] for imp in imported_recipes.values())),
        'data': imported_recipes
    })
