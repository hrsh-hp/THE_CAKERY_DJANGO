from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from cakes.serializers import CakeFullSerializer, CakeHomeSerializer
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
        return JsonResponse(data,status=500)
