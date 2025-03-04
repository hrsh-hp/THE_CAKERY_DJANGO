from django.urls import path,include
from cakes.views import get_home_cake_details

urlpatterns = [
    path('home_cake', get_home_cake_details, name='home_cake'),
]