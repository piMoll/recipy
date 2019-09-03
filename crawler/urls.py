from django.urls import path
from . import views

app_name = 'crawler'
urlpatterns = [
    path('', views.ImportView.as_view(), name='index'),
]
