from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from cakes.serializers import CakeHomeSerializer
from cakes.models import Cake,CakeLike,CakeSize

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
        return JsonResponse(data,status=500)