from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from cakes.serializers import CakeFullSerializer, CakeHomeSerializer, CartSerializer, OrderSerializer
from cakes.models import Cake,CakeLike,CakeSize, Cart, CartItems, Order, Payment, Topping

# Create your views here.
@api_view(['GET'])
def get_home_cake_details(request):
    data = {'data':[],'error':False,'message':None}
    try:
        cakes = Cake.objects.all()
        cakes_serialized = CakeHomeSerializer(cakes,many=True,context={'request':request})
        data['data'] = cakes_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['GET'])
def get_full_cake_details(request, cake_slug):
    data = {'data':[],'error':False,'message':None}
    try:
        cakes = Cake.objects.filter(slug=cake_slug).first()
        if not cakes: raise Exception("Cake not found")
        cakes_serialized = CakeFullSerializer(cakes,context={'request':request})
        data['data'] = cakes_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['GET'])
def get_liked_cake_details(request):
    data = {'data':[],'error':False,'message':None}
    try:
        user = request.user
        cake_likes = CakeLike.objects.filter(user=user,liked=True).select_related('cake')
        if cake_likes.exists(): 
            cakes = [cake_like.cake for cake_like in cake_likes]
            cakes_serialized = CakeHomeSerializer(cakes,many=True,context={'request':request})
            data['data'] = cakes_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def like_cake(request):
    data = {'data':[],'error':False,'message':None}
    try:
        cake_slug = request.data.get('cake_slug')
        liked = request.data.get('liked')
        if not cake_slug or liked is None: raise Exception("Provide cake_slug and liked")
        cake = Cake.objects.filter(slug=cake_slug).first()
        if not cake: raise Exception("Cake not found")
        user = request.user
        if not user: raise Exception("User not found")
        if liked:  # Like the cake
            cake_like, created = CakeLike.objects.get_or_create(user=user, cake=cake)
            cake_like.liked = True
            cake_like.save()
        else:  # Unlike (delete from database)
            # print("unlike")
            CakeLike.objects.filter(user=user, cake=cake).delete()
        data['data'] = {'liked':liked,'likes_count': CakeLike.objects.filter(cake=cake, liked=True).count()}
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)

@api_view(['POST'])
def add_to_cart(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        body = request.data
        if 'cake_slug' not in body or 'size_slug' not in body : raise Exception("Parameters missing")
        cake_slug = body.get('cake_slug')
        size_slug = body.get('size_slug')
        toppings_slugs = request.data.get("toppings", [])
        quantity = int(body.get('quantity',1))
        if quantity < 1: raise Exception("Quantity should be greater than 0")
        cart = Cart.get_or_create_active_cart(user)
        cake = Cake.objects.filter(slug=cake_slug).first()
        if not cake: raise Exception("Cake not found")
        size = CakeSize.objects.filter(slug=size_slug).first()
        if not size: raise Exception("Size not available")
        selected_toppings = list(Topping.objects.filter(slug__in=toppings_slugs))
        existing_cart_items = CartItems.objects.filter(cart=cart, cake=cake, size=size)

        for item in existing_cart_items:
            item_toppings = list(item.toppings.values_list("slug", flat=True))
            if sorted(item_toppings) == sorted(toppings_slugs):
                # Update quantity if exact match found
                item.quantity += quantity
                item.save()
                data['data']['success'] = True
                return JsonResponse(data, status=200)
            
        new_cart_item = CartItems.objects.create(cart=cart, cake=cake, size=size, quantity=quantity)
        new_cart_item.toppings.set(selected_toppings)
        data['data']['success'] = True
        return JsonResponse(data,status=200)
    
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['GET'])
def get_cart_details(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        cart_obj = Cart.objects.filter(user=user,is_ordered=False).first()
        if cart_obj: 
            cart_serialized = CartSerializer(cart_obj,context={'request':request})
            # print(cart_serialized.data)
            data['data'] = cart_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def remove_cart_item(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        body = request.data
        if 'cart_item_slug' not in body: raise Exception("Parameters missing")
        cart_item_slug = body.get('cart_item_slug')
        cart_item = CartItems.objects.filter(slug=cart_item_slug).first()
        if not cart_item: raise Exception("Cart item not found")
        cart = cart_item.cart
        if cart.user != user: raise Exception("Unauthorized")
        cart_item.delete()
        data['data']['success'] = True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def place_order(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        body = request.data
        if 'del_address' not in body or 'payment_method' not in body or 'final_total' not in body: raise Exception("Parameters missing")
        cart = Cart.objects.filter(user=user,is_ordered=False).first()
        if not cart: raise Exception("Active cart not found")
        total_price = body.get('final_total')
        order_obj = Order.objects.create(user=user, cart=cart,total_price=total_price,del_address=body.get('del_address'),status="confirmed")
        payment_method=body.get('payment_method')
        payment_obj = Payment.objects.create(order=order_obj,payment_method=payment_method,is_paid=True if payment_method == "cash" else False)
        cart.is_ordered = True
        cart.save()
        Cart.get_or_create_active_cart(user)
        data['data']['success'] = True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['GET'])
def get_order_details(request):
    data = {'data':[],'error':False,'message':None}
    try:
        user = request.user
        orders = Order.objects.filter(user=user).order_by('created_at').reverse()
        if not orders: raise Exception("No orders found for this user")
        order_serialized = OrderSerializer(orders,many=True,context={'request':request})
        data['data'] = order_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def mark_order_complete(request):
    data = {'data':{},'error':False,'message':None}
    try:
        body = request.data
        if 'order_slug' not in body: raise Exception("Parameters missing")
        order_obj = Order.objects.filter(slug=body['order_slug']).first()
        if not order_obj: raise Exception("Can not find this order")
        order_obj.status = "delivered"
        payment_obj = Payment.objects.get(order=order_obj)
        payment_obj.is_paid=True
        order_obj.save()
        data['data']['success']=True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def mark_order_cancel(request):
    data = {'data':{},'error':False,'message':None}
    try:
        body = request.data
        if 'order_slug' not in body: raise Exception("Parameters missing")
        order_obj = Order.objects.filter(slug=body['order_slug']).first()
        if not order_obj: raise Exception("Can not find this order")
        order_obj.status = "cancelled"
        payment_obj = Payment.objects.get(order=order_obj)
        if payment_obj.payment_method=="cash":
            payment_obj.is_paid=False
        order_obj.save()
        data['data']['success']=True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)