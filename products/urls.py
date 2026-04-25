from django.urls import path, include
from . import views
from .views import create_checkout_session_view

urlpatterns = [
    path('register/', views.register, name='register'),
    
    path('', views.product_list, name='product_list'),

    path('categories/', views.categories, name='categories'),
    path("platforms/<slug:family_slug>/", views.platform_family, name="platform_family"),

    path('platforms/', views.platform_list, name='platform_list'),
    path('platforms/<slug:slug>/', views.platform_detail, name='platform_detail'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<slug:slug>/', views.genre_detail, name='genre_detail'),

    path('<slug:slug>/', views.product_detail, name='product_detail'),

    path("buy/<slug:slug>/", create_checkout_session_view, name="create_checkout_session"),

    path("orders/", include("orders.urls")),
]