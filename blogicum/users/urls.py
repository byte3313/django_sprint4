from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.RegistrationView.as_view(), name='registration'),
]
