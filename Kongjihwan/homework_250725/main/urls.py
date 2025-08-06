from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.main, name='main'),
    path('chatbot/', views.chatbot, name='chatbot')
]