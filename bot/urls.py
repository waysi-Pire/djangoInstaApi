from django.contrib import admin
from django.urls import path,include
from .views import getPostsView

urlpatterns = [
    path('get_posts/',  getPostsView),
]
