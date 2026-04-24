from django.urls import path
from .views import profile_view, profile_edit

urlpatterns = [
    path("edit/", profile_edit, name="profile_edit"),
    path("<slug:slug>/", profile_view, name="profile"),
]
