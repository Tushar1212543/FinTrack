from django.urls import path
from .views import *

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("login-page/", login_page, name="login-page"),
    path("web-login/", web_login, name="web-login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", user_logout, name="logout"),
    path("signup/", signup_page, name="signup"),
    path("profile/", profile_page, name="profile"),
    path("profile/edit/", profile_edit, name="profile-edit"),
    path("profile/delete-picture/", delete_profile_picture, name="delete-profile-picture"),
]
