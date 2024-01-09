from django.urls import path
from .views import FirstStepRegistrationView, FinalizeRegistrationView, LoginView, UserView, LogoutView

urlpatterns = [
    path('registration-first-step', FirstStepRegistrationView.as_view()),
    path('finalize-registration', FinalizeRegistrationView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
]
