from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("command/<int:number>", views.commandpage, name="command"),
    path("commands", views.commands, name="commands"),
    path("command/<int:number>/addproduct", views.addproduct, name="addproduct"),
    path("logout/", views.logout, name="logout"),
]
