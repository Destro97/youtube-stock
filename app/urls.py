from django.urls import path

from . import views

urlpatterns = [
    path('', views.fetch),
    path('search', views.search)
]