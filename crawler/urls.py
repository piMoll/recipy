from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImportView.as_view(), name='index'),
]
