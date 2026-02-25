from django.urls import path
from . import views

urlpatterns = [
    path('platforms/', views.platform_list, name='platform_list'),
    path('platforms/<slug:slug>/', views.platform_detail, name='platform_detail'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<slug:slug>/', views.genre_detail, name='genre_detail'),
    path('categories/', views.categories, name='categories'),
]