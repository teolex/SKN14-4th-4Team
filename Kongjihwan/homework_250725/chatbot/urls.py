# from django.urls import path
# from . import views

# app_name = 'chatbot'

# urlpatterns = [
#     # path(url, view_function, name)
#     path('main/', views.index, name='index'),
#     path('chatbot/', views.index, name='chatbot'),
#     path('chatbot/question/<int:id>', views.question, name='question'),
# ]

# analyzer/urls.py

from django.urls import path
from . import views

# 앱의 URL 패턴을 정의합니다.
urlpatterns = [
    path('chat/', views.index, name='index'), # html 응답
    
]