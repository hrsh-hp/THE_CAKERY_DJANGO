from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import AllowAny

from Auth.models import CustomUser
from .serializers import LoginSerializer
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
        data['data']['user']={"email":authenticated_user.email,"name":f"{authenticated_user.first_name}" if user.first_name else None,"slug":authenticated_user.slug}
        print(data)
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)