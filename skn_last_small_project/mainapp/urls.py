from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as auth_views
from .                   import views

app_name = 'mainapp'

urlpatterns = [
    path(''         , views.intro, name="intro"),
    path('main/'    , views.main, name="main"),
    path('chat/'    , views.chat, name="chat"),

    path('login/'   , auth_views.LoginView.as_view(template_name="mainapp/login.html"), name="login"),
    path('signup/'  , views.signup, name="signup"),
    path('logout/'  , views.logout, name="logout"),

    path('mypage/'  , views.mypage, name="mypage"),
]

# 업로드 파일 경로설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)