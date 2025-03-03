from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import AllowAny

from Auth.models import CustomUser
from Auth.serializers import UserSerializer
from django.contrib.auth import authenticate

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
        token, created = Token.objects.get_or_create(user=authenticated_user)
        data['data']['token']=token.key
        user_serialized = UserSerializer(authenticated_user,context={'request':request})
        data['data']['user']=user_serialized.data
        print(data)
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
        if 'email' not in body or 'password' not in body: raise Exception("Parameters Missing")
        email = body['email']
        password = body['password']
        user, created = CustomUser.objects.get_or_create(email=email)
        if created:
            user.set_password(password)
            user.save()
        else:
            raise Exception("User with this email already exists!")
        # user_serialized = UserSerializer(user,context={'request':request})
        # data['data']['user']=user_serialized.data
        data['data']['success'] = True
        print(data)
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
        print(request.user)
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)    
    
