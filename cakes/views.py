import json
import random
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from Auth.models import DeliveryPerson
from cakes.serializers import CakeFullSerializer, CakeHomeSerializer, CartSerializer, OrderSerializer, ReviewSerializer, ToppingsSerializer
from cakes.models import Cake,CakeLike,CakeSize, Cart, CartItems, Order, Payment, Review, Topping
from django.core.files.storage import default_storage

# Create your views here.
@api_view(['POST'])
def add_cake(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        if user.role != "admin": raise Exception("Unauthorized")
        body = request.data
        # print(body)
        if 'name' not in body or "description" not in body or "sizes" not in body: raise Exception("Parameters missing")
        name = body.get('name')
        description = body.get("description")
        available_toppings = body.get("available_toppings", "false").lower() in ["true", "1"]
        toppings_slugs = json.loads(body.get("toppings", []))
        sizes_data = json.loads( body.get("sizes"))
        image = request.FILES.get("image")
        image_path = None
        if image: image_path = default_storage.save(f"images/cakes/{image.name}", image)
        cake_obj = Cake.objects.create(
            name=name,
            description=description,
            available_toppings=available_toppings,
            image=image_path
        )
        for size in sizes_data:
            if "size" in size and "price" in size:
                CakeSize.objects.create(cake=cake_obj, size=size["size"], price=size["price"])
        valid_toppings = Topping.objects.filter(slug__in=toppings_slugs)
        cake_obj.toppings.set(valid_toppings)
        cake_obj.save()
        data['data']['success'] = True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)


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
def get_toppings(request):
    data = {'data':[],'error':False,'message':None}
    try:
        if request.user.role != "admin": raise Exception("Unauthorized")
        toppings_obj = Topping.objects.all()    
        toppings_serialized = ToppingsSerializer(toppings_obj,many=True)
        data['data'] = toppings_serialized.data
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
        order_obj.delivery_person = random.choice(DeliveryPerson.objects.all())
        order_obj.save()
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
        # if not orders: raise Exception("No orders found for this user")
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
    
@api_view(['POST'])
def submit_review(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        body = request.data
        if 'order_slug' not in body or 'rating' not in body or 'delivery_person_slug' not in body: raise Exception("Missing required parameters")
        print(body)
        order_obj = Order.objects.filter(slug=body['order_slug'],user=user).first()
        if not order_obj: raise Exception("Order not found or Unauthorized")
        if order_obj.status != "delivered": raise Exception("Review can be submitted only for delivered orders")
        # delivery_person = DeliveryPerson.objects.filter(slug=body['delivery_person_slug']).first()
        # if not delivery_person: raise Exception("Delivery person not found")
        review, created = Review.objects.get_or_create(
            order=order_obj,
            user=user,
            defaults={
                "rating": int(float(body["rating"])),
                "review_text": body.get("feedback", ""),
                "tags": body.get("tags", [])
            }
        )
        if not created:raise Exception("Review already submitted for this order")
        data['data']['success']=True
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['GET'])
def get_review_details(request,order_slug):
    data = {'data':[],'error':False,'message':None}
    try:
        user = request.user
        order_obj = Order.objects.filter(user=user,slug=order_slug).first()
        if not order_obj: raise Exception("No orders found")
        review_obj = Review.objects.filter(order=order_obj).first()
        if not review_obj: raise Exception("No review found for this order")
        review_serialized = ReviewSerializer(review_obj,context={'request':request})
        data['data'] = review_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)