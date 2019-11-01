from django.shortcuts import redirect, get_object_or_404
from django.urls import path, include

from recipes.models import Recipe, Collection
from . import views

app_name = 'recipes'


def r(model):
    def view(*args, **kwargs):
        return redirect(get_object_or_404(model, **kwargs))
    return view


collection_urlpatterns = [
    path('', views.CollectionOverviewView.as_view(), name='list'),
    path('<int:pk>/', r(Collection), name='short'),
    path('<int:pk>/edit/', views.CollectionEditView.as_view(), name='edit'),
    path('<int:pk>/<slug:slug>/', views.CollectionDetailsView.as_view(), name='detail'),
    path('public/<slug:slug>/', views.CollectionDetailsPublicView.as_view(), name='public'),
    path('create/', views.CollectionEditView.as_view(), name='create'),
]

urlpatterns = [
    path('', views.SearchPageView.as_view(), name='search'),
    path('<int:pk>/', r(Recipe), name='short'),
    path('<int:pk>/edit/', views.create, name='edit'),
    path('<int:pk>/<slug:slug>/', views.RecipeDetailsView.as_view(), name='detail'),
    path('public/<slug:slug>/', views.RecipeDetailsPublicView.as_view(), name='public'),

    path('create/', views.create, name='create'),
    path('search/', views.SearchView.as_view(), name='search_api'),

    path('collections/', include((collection_urlpatterns, 'collections')))
]
