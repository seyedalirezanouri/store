from django.urls import path
from .views import UserRegistrationView, LoginView, LogoutView, ChangePasswordView, SetProfileView, GetProfileView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='Register'),
    path("login/" , LoginView.as_view(), name='Login'),
    path("logout/", LogoutView.as_view(), name='Logout'),
    path('change-password/', ChangePasswordView.as_view(), name='Change password'),
    path('set-profile/', SetProfileView.as_view(), name='Set Profile'),
    path('get-profile/', GetProfileView.as_view(), name='Get Profile'),
]