from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.urls import include
from products import views as products_views

urlpatterns = [
    path('', products_views.product_list, name='home'),
    path('products/', include('products.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]