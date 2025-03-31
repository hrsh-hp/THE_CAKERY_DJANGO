import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import AllowAny

from Auth.models import Address, CustomUser, DeliveryPerson
from Auth.serializers import UserSerializer,FullUserDetailsSerializer
from django.contrib.auth import authenticate

from cakes.models import Cart

# Create your views here.

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def LoginView(request):
    data = {'data':{},'error':False,'message':None}
    try:    
        body = request.data
        if 'email' not in body or 'password' not in body: raise Exception("Parameters Missing")
        email = body['email']
        password = body['password']
        user = CustomUser.objects.get(email=email)
        if not user: raise Exception("User with this email does not exist!")
        authenticated_user = authenticate(email=user.email,password=password)
        if not authenticated_user: raise Exception("Incorrect Email or Password!!")
        Cart.get_or_create_active_cart(user=authenticated_user)
        token, created = Token.objects.get_or_create(user=authenticated_user)
        data['data']['token']=token.key
        user_serialized = UserSerializer(authenticated_user,context={'request':request})
        data['data']['user']=user_serialized.data
        # print(data)
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)
    
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    data = {'data':{},'error':False,'message':None}
    try:    
        body = request.data
        if 'email' not in body or 'password' not in body and 'role' not in body: raise Exception("Parameters Missing")
        role = body['role']
        body['vehicle_number'] = "GJ01XV3535"
        email = body['email']
        password = body['password']
        first_name = body.get('first_name', '')
        last_name = body.get('last_name', '')
        phone_no = body.get('phone', '')
        user, created = CustomUser.objects.get_or_create(email=email,first_name=first_name,last_name=last_name,phone_no=phone_no,role=role) 

        if created:
            user.is_verified = True
            user.set_password(password)
            user.save()
        else:
            raise Exception("User with this email already exists!")
        if role == 'delivery_person':
            delivery_person, created= DeliveryPerson.objects.get_or_create(user=user).first()
            if not created: 
                raise Exception("Delivery account with this user already exists!")
            delivery_person.vehicle_number = body.get('vehicle_number', '')
            user.is_verified = True
            user.save()
        # user_serialized = UserSerializer(user,context={'request':request})
        # data['data']['user']=user_serialized.data
        data['data']['success'] = True
        # print(data)
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)

@api_view(['GET'])
def get_user_details(request):
    data = {'data':{},'error':False,'message':None}
    try:
        if not request.user.is_authenticated: raise Exception("User not logged in")
        user_obj = CustomUser.objects.filter(email=request.user.email).first()
        if not user_obj: raise Exception("User not found")
        user_serialized = FullUserDetailsSerializer(user_obj,context={'request':request})
        data['data']['user']=user_serialized.data
        # print(data)
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)    
    
@api_view(['POST'])
def update_profile(request):
    data = {'data':{},'error':False,'message':None}
    try:
        if not request.user.is_authenticated: raise Exception("User not logged in")
        user_obj = CustomUser.objects.filter(email=request.user.email).first()
        if not user_obj: raise Exception("User not found")
        body = request.POST
        # print(body)
        if not all(key in body for key in ['first_name', 'last_name', 'phone_no', 'address']):
            raise Exception("Parameters Missing")
        user_obj.first_name = body.get('first_name', '')
        user_obj.last_name = body. get('last_name', '')
        user_obj.phone_no = body.get('phone_no', '')
        if 'user_image' in request.FILES:
            user_obj.user_image = request.FILES.get('user_image', None)

        address_obj, _ = Address.objects.get_or_create(user=user_obj)
        try:
            # print(body['address'])
            address_data = json.loads(body['address'])
            address_obj.address_text = address_data.get('address_text', '')
            address_obj.longitude = address_data.get('longitude', 0.0)
            address_obj.latitude = address_data.get('latitude', 0.0)
        except json.JSONDecodeError:
            raise Exception("Invalid address format")

        address_obj.save()
        user_obj.save()
        user_serialized = UserSerializer(user_obj,context={'request':request})
        data['data']['success']=True
        data['data']['user']=user_serialized.data
        # print(data)
        return JsonResponse(data, status=200)  
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)  
