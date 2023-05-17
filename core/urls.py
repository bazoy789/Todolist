
from django.urls import path

from views import RegistrationView, LoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path("sinnup/", RegistrationView.as_view(), name="sinnup"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("update_password/", UpdatePasswordView.as_view(), name="update_password"),
]
