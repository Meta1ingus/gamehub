from django.urls import path
from . import views

urlpatterns = [
    path("success/", views.success, name="checkout_success"),
    path("cancel/", views.cancel, name="checkout_cancel"),
]
