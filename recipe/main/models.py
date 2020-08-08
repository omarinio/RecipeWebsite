from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Recipe(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="poster")
    title = models.TextField(blank=False, default="falo")
    body = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", blank=True)
    picture = models.ImageField(upload_to='uploads/', verbose_name='image')

class Follow(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followed")
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

class Comment(models.Model):
    comment = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Commenter")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ListComment")
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Liker")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="LikedRecipe")