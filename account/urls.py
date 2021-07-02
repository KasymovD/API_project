from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.RegistrationView.as_view()),
    path('activation/', views.ActivationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('reset_password/', views.ResetPasswordView.as_view()),
    path('reset_password_complete/', views.ResetPasswordCompeteView.as_view()),
    path('change_password/', views.ChangePasswordView.as_view()),
    path('profile/', views.ProfileView.as_view()),
]
