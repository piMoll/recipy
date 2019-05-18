from django.shortcuts import render
from django.http import HttpResponse
from recipes.models import Tag


def index(request):
    tags = Tag.objects.all()
    html = f"""
    <html>
        <head>
            <style>
                ul {{list-style-type:none;}}
                .tag {{border-radius:5px;display:inline-block;margin:3px;padding:3px 5px}}
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
