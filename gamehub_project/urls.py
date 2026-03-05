from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from products import views as products_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path('products/', include('products.urls')),
    path('admin/', admin.site.urls),

    # Django's built-in login/logout/password views
    path('accounts/', include('django.contrib.auth.urls')),

    # Custom registration view
    path('accounts/register/', products_views.register, name='register'),
    
    # Cart URLs
    path('cart/', include('cart.urls')),
]