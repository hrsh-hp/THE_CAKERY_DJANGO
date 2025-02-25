from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer
# Create your views here.

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def LoginView(request):
    data = {'data':{},'error':False,'message':None}
    try:
        body = request.data
        serialzed_data = LoginSerializer(data=body)
        if not serialzed_data.is_valid():
            raise Exception(serialzed_data.errors)
        print(serialzed_data.validated_data)
        user = serialzed_data.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        data['data']['token']=token.key
        data['data']['slug']=user.slug
        return JsonResponse(data,status=200)
    except Exception as e:
        print(e)
        data['error'] = True
        data['message'] = str(e)
        return JsonResponse(data, status=500)