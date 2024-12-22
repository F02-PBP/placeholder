from django.urls import path
from authentication.views import login, register, logout, check_auth_status

app_name = 'authentication'

urlpatterns = [
    path('flutter-login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('check_auth_status/', check_auth_status, name='check_auth_status'),
]