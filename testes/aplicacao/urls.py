from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("command/<int:number>", views.commandpage, name="command"),
    path("commands", views.commands, name="commands"),
    path("logout/", views.logout, name="logout"),
    path("commands/<int:number>/neworder/", views.neworder, name="neworder"),
    path("commands/<int:number>/neworder/<int:cod>", views.category, name="category"),
    path("commands/<int:number>/neworder/revision", views.orderrevision, name="orderrevision"),
    path("commands/<int:number>/neworder/<int:cod>/<str:product>/<str:printer>", views.categorysizes, name="categorysizes"),

    
]
