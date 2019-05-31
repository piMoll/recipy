from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('<int:pk>', views.RecipeDetailsView.as_view(), name='recipe_detail'),
    path('search/', views.search, name='search'),
]
