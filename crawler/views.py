from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from crawler.crawler import import_recipe, simple_get


def index(request):
    return JsonResponse(import_recipe('holunderblüten fizz'))

