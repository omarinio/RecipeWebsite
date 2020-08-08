from django.contrib import admin
from .models import Recipe, User, Follow, Comment, Like

# Register your models here.

admin.site.register(Recipe)
admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)