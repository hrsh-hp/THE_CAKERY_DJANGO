from rest_framework import serializers
from django.db import models

from cakes.models import Cake, CakeLike, CakeSize

class CakeHomeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Cake
        fields = ['name','slug','image_url','price','liked','likes_count']

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_price(self, obj):
    # Get the minimum price from CakeSize model
        min_price = obj.sizes.aggregate(min_price=models.Min('price'))['min_price']
        return min_price if min_price is not None else 0.00
    
    def get_liked(self, obj):
        # Check if the user has liked this cake
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return CakeLike.objects.filter(user=user, cake=obj, liked=True).exists()
        return False
    
    def get_likes_count(self, obj):
        return obj.likes.filter(liked=True).count()
    
class SizesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CakeSize
        fields = ['size','price']

class CakeFullSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    sizes = SizesSerializer(many=True)

    class Meta:
        model = Cake
        fields = ['name','slug','image_url','liked','likes_count','description','available_toppings','sizes']

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_liked(self, obj):
        # Check if the user has liked this cake
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return CakeLike.objects.filter(user=user, cake=obj, liked=True).exists()
        return False
    
    def get_likes_count(self, obj):
        return obj.likes.filter(liked=True).count()
    
