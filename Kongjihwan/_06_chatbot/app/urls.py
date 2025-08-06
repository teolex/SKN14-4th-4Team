from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
  
  path('', views.index, name='index'), # html 응답
  
  path('init_chat', views.init_chat, name='init_chat'), # json 응답
  path('chat', views.chat, name='chat'),
  path('del_chat', views.del_chat, name='del_chat'),
]