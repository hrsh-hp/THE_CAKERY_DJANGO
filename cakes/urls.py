from django.urls import path,include
from cakes.views import get_home_cake_details,get_full_cake_details,like_cake,get_liked_cake_details,add_to_cart,get_cart_details

urlpatterns = [
    path('home_cake', get_home_cake_details, name='home_cake'),
    path('liked_cake', get_liked_cake_details, name='liked_cake'),
    path('full_cake/<str:cake_slug>', get_full_cake_details, name='full_cake'),
    path('like/',like_cake,name='like_cake'),
    path('cart',get_cart_details,name='get_cart_details'),
    path('cart/add/',add_to_cart,name='add_to_cart'),
]