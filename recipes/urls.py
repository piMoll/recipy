from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.SearchPageView.as_view(), name='search'),
    path('<int:pk>', views.RecipeShortDetailsView.as_view(), name='short'),
    path('<int:pk>/<slug:slug>', views.RecipeDetailsView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.create, name='edit'),
    path('create/', views.create, name='create'),
    path('public/<slug:slug>', views.RecipeDetailsPublicView.as_view(), name='public'),
    path('search/', views.SearchView.as_view(), name='search_api'),
    path('collections', views.CollectionOverviewView.as_view(), name='collection_list'),
    path('collections/<int:pk>', views.CollectionDetailsView.as_view(), name='collection_detail'),
]
