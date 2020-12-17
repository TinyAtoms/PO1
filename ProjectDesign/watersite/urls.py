from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.group_list, name='group-list'),
    path('water_plantgroup/<int:location>', views.water_pg,
         name='series-detail-view'),
    path("check/", views.check_waterlevel, name="check-waterlevel"),
    path("create_evap/", views.create_evap, name="create-evap")
]
