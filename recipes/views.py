from django.shortcuts import render
from django.http import HttpResponse
from recipes.models import Recipe

def index(request):
    return HttpResponse(f'There are {Recipe.objects.count()} Recipes')
