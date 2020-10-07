
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
    path("comment", views.comment, name="comment"),
    path("create", views.create, name="create"),
    path("user/<username>", views.user, name="user"),
    path("follow", views.follow),
    path("liked", views.view_liked, name="view_liked"),
    path("like", views.like_recipe),
    path("search", views.search, name="search"),
    path("recipes/delete/<int:id>", views.delete, name="delete"),
    path("recipes/edit/<int:id>", views.edit_recipe, name="edit"),
    path("recipes/following", views.following, name="following")
]