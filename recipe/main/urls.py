
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("recipes", views.recipes, name="recipes"),
    path("about", views.about, name="about"),
    path("recipes/<int:id>", views.recipe_view, name="recipe"),
    path("comment", views.comment, name="comment")
]