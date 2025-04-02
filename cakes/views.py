from decimal import Decimal
import json
import random
from tokenize import Double
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from Auth.models import CustomUser, DeliveryPerson
from cakes.serializers import CakeExtraSerializer, CakeFullModificationsSerializer, CakeFullSerializer, CakeHomeSerializer, CakeSpongeSerializer, CartSerializer, OrderSerializer, ReviewSerializer, ToppingsSerializer
from cakes.models import Cake, CakeExtra,CakeLike,CakeSize, Cart, CartItems, CustomModification, Order, Payment, Review, Topping, CakeSponge
from django.core.files.storage import default_storage
from django.db import transaction

# Create your views here.
@api_view(['POST'])
def add_cake(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        print(user.role)
        if user.role != "admin" and user.role !='user': raise Exception("Unauthorized")
        body = request.data
        # print(body)
        if 'name' not in body or "description" not in body or "sizes" not in body and 'sponge' not in body: raise Exception("Parameters missing")
        name = body.get('name')
        sponge = body.get('sponge')
        if sponge:
            sponge_obj = CakeSponge.objects.filter(slug=sponge).first()
            if not sponge_obj: raise Exception("Sponge not found")
        else:
            raise Exception("Sponge not given")
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
            image=image_path,
            sponge=sponge_obj,
            user = user
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

@api_view(['POST'])
def edit_cake(request):
    data = {'data':{},'error':False,'message':None}
    try:
        user = request.user
        if user.role != "admin": raise Exception("Unauthorized")
        body = request.data
        print(body)
        if 'slug' not in body: raise Exception("Parameters missing")
        name = body.get('name')
        sponge = body.get('sponge')
        if sponge:
            sponge_obj = CakeSponge.objects.filter(slug=sponge).first()
            if not sponge_obj: raise Exception("Sponge not found")
        else:
            raise Exception("Sponge not given")
        description = body.get("description")
        available_toppings = body.get("available_toppings", "false").lower() in ["true", "1"]
        toppings_slugs = json.loads(body.get("toppings", []))
        sizes_data = json.loads( body.get("sizes",'[]'))
        image = request.FILES.get("image")
        print(image)
        image_path = None
        cake_obj = Cake.objects.filter(slug=body['slug']).first()
        if not cake_obj: raise Exception("Cake not found")
        cake_obj.name = name
        cake_obj.description = description
        cake_obj.available_toppings = available_toppings
        if image is not None: 
            image_path = default_storage.save(f"images/cakes/{image.name}", image)
            cake_obj.image = image_path
        cake_obj.sponge = sponge_obj
        cake_obj.save()
        cake_obj.sizes.all().delete()
        for size in sizes_data: 
            if "size" in size and "price" in size:
                print(size)
                CakeSize.objects.create(cake=cake_obj, size=size["size"], price=Decimal(size["price"]))
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
        admin_users = CustomUser.objects.filter(role='admin')
        current_user = CustomUser.objects.filter(email=request.user.email)
        users = admin_users | current_user
        cakes = Cake.objects.filter(user__in = users)
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
def get_cake_details_for_modification(request):
    data = {'data':[],'error':False,'message':None}
    try:
        # cakes = Cake.objects.filter(slug=cake_slug).first()
        toppings = Topping.objects.all()
        sponge = CakeSponge.objects.all()
        # if not cakes: raise Exception("Cake not found")
        # print(cakes)
        cakes_modification_serialized = CakeFullModificationsSerializer({"toppings": toppings,"sponges":sponge}, context={"user": request.user,'request':request})
        data['data'] = cakes_modification_serialized.data
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
        # if request.user.role != "admin": raise Exception("Unauthorized")
        toppings_obj = Topping.objects.all()    
        toppings_serialized = ToppingsSerializer(toppings_obj,many=True)
        data['data'] = toppings_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def add_toppings(request):
    data = {'data':{},'error':False,'message':None}
    try:
        if request.user.role != "admin": raise Exception("Unauthorized")
        body = request.data
        if 'name' not in body or 'price' not in body: raise Exception("Parameters missing")
        print(body)
        name = body.get('name')
        price = body.get('price')
        slug = body.get('slug')
        if slug:
            topping_obj = Topping.objects.filter(slug=slug).first()
            if not topping_obj: raise Exception("Topping not found")
            topping_obj.name = name
            topping_obj.price = price
            topping_obj.save()
        else:   
            topping_obj = Topping.objects.create(name=name,price=price)
        data['data']['success'] = True
        data['data']['topping'] = ToppingsSerializer(topping_obj).data
        return JsonResponse(data,status=200) 
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)  
    
@api_view(['GET'])
def get_sponges(request):
    data = {'data':[],'error':False,'message':None}
    try:
        # if request.user.role != "admin": raise Exception("Unauthorized")
        sponges_obj = CakeSponge.objects.all()
        sponges_serialized = CakeSpongeSerializer(sponges_obj,many=True)
        data['data'] = sponges_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def add_sponges(request):
    data = {'data':{},'error':False,'message':None}
    try:
        if request.user.role != "admin": raise Exception("Unauthorized")
        body = request.data
        # print(body)
        if 'name' not in body or 'price' not in body: raise Exception("Parameters missing")
        name = body.get('name')
        price = body.get('price')
        slug = body.get('slug')
        if slug:
            sponge_obj = CakeSponge.objects.filter(slug=slug).first()
            if not sponge_obj: raise Exception("Sponge not found")
            sponge_obj.sponge = name 
            sponge_obj.price = price
            sponge_obj.save()
        else:   
            sponge_obj = CakeSponge.objects.create(sponge=name,price=price)
        data['data']['success'] = True
        data['data']['sponge'] = CakeSpongeSerializer(sponge_obj).data
        return JsonResponse(data,status=200) 
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500) 
    
@api_view(['GET'])
def get_extras(request):
    data = {'data':[],'error':False,'message':None}
    try:
        # if request.user.role != "admin": raise Exception("Unauthorized")
        cake_extra_objs = CakeExtra.objects.all()
        cake_extra_objs_serialized = CakeExtraSerializer(cake_extra_objs,many=True)
        data['data'] = cake_extra_objs_serialized.data
        return JsonResponse(data,status=200)
    except Exception as e:
        data['error'] = True
        data['message'] = str(e)
        print(e)
        return JsonResponse(data,status=500)
    
@api_view(['POST'])
def add_extras(request):
    data = {'data':{},'error':False,'message':None}
    try:
        if request.user.role != "admin": raise Exception("Unauthorized")
        body = request.data
        if 'name' not in body or 'price' not in body and 'category' not in body: raise Exception("Parameters missing")
        name = body.get('name')
        price = body.get('price')
        category = body.get('category')
        slug = body.get('slug')
        if slug:
            extra_obj = CakeExtra.objects.filter(slug=slug).first()
            if not extra_obj: raise Exception("Extra not found")
            extra_obj.name = name
            extra_obj.price = price
            extra_obj.category = category
            extra_obj.save()
        else:
            extra_obj = CakeExtra.objects.create(name=name,price=price,category=category)
        data['data']['success'] = True
        data['data']['extra'] = CakeExtraSerializer(extra_obj).data
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
        if user.role == "admin": 
            orders = Order.objects.all().order_by('created_at').reverse()
        elif user.role == "delivery_person":
            orders = Order.objects.filter(delivery_person__user=user).order_by('created_at').reverse()
        else:
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
        if request.user.role == 'delivery_person':
            if order_obj.delivery_person.user != request.user: raise Exception("Unauthorized")
        if not order_obj: raise Exception("Can not find this order")
        if 'delivery_confirmation_code' in body:
            delivery_confirmation_code = body.get('delivery_confirmation_code')
        status = body.get('status')
        if order_obj.status == 'confirmed' and status == 'out_for_delivery':
            order_obj.status = status
        elif order_obj.status == 'out_for_delivery' and status == 'delivered':
            if not delivery_confirmation_code: raise Exception("Delivery confirmation code missing")
            if order_obj.slug.split('_')[0] == delivery_confirmation_code:
                order_obj.status = status
                payment_obj = Payment.objects.get(order=order_obj)
                payment_obj.is_paid=True
            else: raise Exception("Invalid confirmation code")
        else: raise Exception(f"Invalid status change {status} from {order_obj.status}")
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
    
@api_view(['POST'])
def add_modified_to_cart(request):
    data = {'data': {}, 'error': False, 'message': None}
    try:
        user = request.user
        body = request.data
        if 'size' not in body or 'sponge_slug' not in body:
            raise ValueError("Missing required parameters: 'size' or 'sponge_slug'")

        size = body.get("size")
        sizes = {
                    '0.3': 120.0, 
                    '0.5': 200.0, 
                    '1.0': 400.0, 
                    '1.5': 600.0, 
                    '2.0': 800.0, 
                    '2.5': 1000.0, 
                    '3.0': 1200.0, 
                    '3.5': 1400.0, 
                    '4.0': 1600.0
                }
        price = sizes.get(size, "Invalid size selected")  # Handles missing keys gracefully
        if price == "Invalid size selected":
            print("Error: The selected size is not available.")
        else:
            print(f"Price: {price}")
        sponge_slug = body.get("sponge_slug")
        quantity = int(body.get("quantity", 1))
        toppings = json.loads(body.get("toppings", []))
        extras_dict = body.get("extras", {})
        user_request = body.get("user_request", "")
        cake_image = request.FILES.get("cake_image")
        sponge_obj = CakeSponge.objects.filter(slug=sponge_slug).first()
        cake_name = f"Custom {sponge_obj.sponge} Cake"
        topping_objs = Topping.objects.filter(slug__in=toppings)
        if not sponge_obj:
            raise ValueError(f"Invalid sponge_slug: '{sponge_slug}' not found")

        # Validate and parse extras_dict if needed
        if not isinstance(extras_dict, dict):
            try:
                extras_dict = json.loads(extras_dict)
            except json.JSONDecodeError:
                raise ("Invalid format for 'extras'. Expected JSON object.")
        extras_slugs = [slug for category in extras_dict.values() for slug in category]
        extras_objs = CakeExtra.objects.filter(slug__in=extras_slugs)
        extras_price = sum(extra.price for extra in extras_objs)
        # Atomic transaction to ensure consistency
        with transaction.atomic():
            # Create the cake object
            cake = Cake.objects.create(
                name=cake_name,
                description=user_request,
                image=cake_image,
                user=user,
                sponge=sponge_obj,
            )
            cake.toppings.set(topping_objs)
            cake_size = CakeSize.objects.create(cake=cake, size=size, price=price)
            cart = Cart.get_or_create_active_cart(user)
            modification = CustomModification.objects.create(
                user=user,
                cake=cake,
                special_requests=user_request,
                total_price=extras_price
            )
            modification.extras.set(extras_objs)
            new_cart_item = CartItems.objects.create(
                cart=cart, cake=cake, size=cake_size, quantity=quantity,custom_modification=modification
            )
            new_cart_item.toppings.set(topping_objs)
            new_cart_item.save()
        data['data']['success'] = True
        return JsonResponse(data, status=200)

    except Exception as e:  # Handle unexpected errors
        data['error'] = True
        data['message'] = "Something went wrong: " + str(e)
        print(e)
        return JsonResponse(data, status=500)