from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("commands/<int:number>", views.commandpage, name="command"),
    path("commands", views.commands, name="commands"),
    path("logout/", views.logout, name="logout"),
    path("commands/<int:number>/neworder/", views.neworder, name="neworder"),
    path("commands/<int:number>/neworder/<int:cod>", views.category, name="category"),
    path("commands/<int:number>/neworder/revision", views.orderrevision, name="orderrevision"),
    path("commands/<int:number>/neworder/<int:cod>/<str:product>/<str:printer>", views.categorysizes, name="categorysizes"),
    path("commands/<int:number>/neworder/revision/<int:cod>", views.edittext, name="edittext"),
    path("commands/<int:number>/neworder/division", views.divisionpage, name="divisionpage"),
    path("commands/<int:number>/addclient", views.addclient, name="addclient"),
    path("commands/<int:number>/neworder/send", views.sendorder, name="sendorder"),
    path("commands/<int:number>/addclient/send", views.sendclient, name="sendclient"),
    
]
