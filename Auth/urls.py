from django.urls import path,include
from rest_framework.authtoken .views import obtain_auth_token
from .views import LoginView,get_user_details,register_view

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path("login/",LoginView,name="login"),
    path("register/",register_view,name="register"),
    path('get_user_details/',get_user_details,name="get_user_details"),
]