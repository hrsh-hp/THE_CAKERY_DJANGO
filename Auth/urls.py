from django.urls import path,include
from rest_framework.authtoken .views import obtain_auth_token
from .views import LoginView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path("login/",LoginView,name="login"),
]