from django.contrib import admin
from django.urls import path,include
from .views import signinView,signupView


urlpatterns = [
    path('signup/', signupView, name='signup'),
    path("signin/", signinView)
]
