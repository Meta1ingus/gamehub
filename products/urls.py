from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    
    path('', views.product_list, name='product_list'),

    path('categories/', views.categories, name='categories'),

    path('platforms/', views.platform_list, name='platform_list'),
    path('platforms/<slug:slug>/', views.platform_detail, name='platform_detail'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<slug:slug>/', views.genre_detail, name='genre_detail'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:game_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:game_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:game_id>/', views.cart_update, name='cart_update'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),

    path('<slug:slug>/', views.product_detail, name='product_detail'),

]