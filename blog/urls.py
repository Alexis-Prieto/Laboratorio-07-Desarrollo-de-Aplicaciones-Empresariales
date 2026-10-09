"""URLs for the blog app."""
from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.front_page, name="front_page"),
]
