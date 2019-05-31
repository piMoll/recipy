from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>', views.RecipeDetailsView.as_view(), name='recipe_detail'),
    path('search/', views.search, name='search'),
]
