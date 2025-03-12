from django.urls import path,include
from cakes.views import add_cake,get_home_cake_details,get_full_cake_details,like_cake,get_toppings,get_liked_cake_details,add_to_cart,get_cart_details,remove_cart_item,place_order,get_order_details,mark_order_cancel,mark_order_complete,submit_review,get_review_details

urlpatterns = [
    path('add/',add_cake,name='add_cake'),
    path('home_cake', get_home_cake_details, name='home_cake'),
    path('liked_cake', get_liked_cake_details, name='liked_cake'),
    path('full_cake/<str:cake_slug>', get_full_cake_details, name='full_cake'),
    path('like/',like_cake,name='like_cake'),
    path('toppings',get_toppings,name='get_toppings'),
    path('cart',get_cart_details,name='get_cart_details'),
    path('cart/add/',add_to_cart,name='add_to_cart'),
    path('cart/remove/',remove_cart_item,name='remove_cart_item'),
    path('cart/place_order/',place_order,name='place_order'),
    path('orders',get_order_details,name='get_order_details'),
    path('orders/cancel/',mark_order_cancel,name="cancle_order"),
    path('orders/complete/',mark_order_complete,name="compelete_order"),
    path('orders/review/',submit_review,name="review_order"),
    path('orders/review/<str:order_slug>',get_review_details,name="get_review_order"),

]