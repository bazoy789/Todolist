from django.urls import path, include

from bot import views

urlpatterns = [
    path('verify', views.VerificationView.as_view(), name="verify")
]