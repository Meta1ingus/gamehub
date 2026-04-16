from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from products import views as products_views
from checkout.webhooks import stripe_webhook

urlpatterns = [
    path("", core_views.home, name="home"),
    path('products/', include('products.urls')),
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', products_views.register, name='register'),

    path('cart/', include('cart.urls')),
    path("checkout/", include("checkout.urls")),

    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
]