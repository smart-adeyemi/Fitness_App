from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', login, name="login"),
    path('Logout', logout, name="logout"),
    path('Create_Profile/', Create_Profile, name="create_profile"),
    path('Profile/', View_Profile, name="view_profile"),
    path('Profile/Update/', Update_Profile, name="update_profile"),
    path('Profile/Change_password', Change_Password, name="change_password"),
    path('Home/', Home, name="homepage"),
    path('Journal/', Journal, name="journal"),
    path('Journal/Log_Food', Log_Food, name="log_food"),
    path('Journal/Add_Food', Journal, name="add_food"),
    path('Exercise/', Exercise_Page, name="exercise"),
    path('Exercise/Log_Exercise', Log_Exercise, name="log_exercise"),
    path('Exercise/Add_Exercise', Exercise_Page, name="add_exercise"),
    path('Stats/', Stats, name='stats'),
    path('Settings/', Settings, name="settings"),
]