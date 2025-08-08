from django.urls import path
from . import views
from .views import signup_view
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.chat, name="chat"),
    path("login/", LoginView.as_view(template_name='uauth/login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page='home'), name='logout'),
    path("signup/",  signup_view, name="signup"),
    path("mypage/", views.mypage, name="mypage"),
    path("mypage/edit/", views.mypage_edit, name="mypage_edit"),
    
]

