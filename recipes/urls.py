from django.urls import path
from . import views

app_name = 'recipes'
urlpatterns = [
    path('<int:pk>', views.RecipeDetailsView.as_view(), name='recipe_detail'),
    # path('<int:pk>/edit/', RecipeEditView.as_view(), name='edit'),
    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),
]
