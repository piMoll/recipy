from django.urls import path
from . import views
from recipes.views import RecipeDetailsView

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>', RecipeDetailsView.as_view(), name='detail'),
]