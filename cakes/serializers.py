from rest_framework import serializers
from django.db import models

from cakes.models import Cake, CakeLike, CakeSize, Cart, CartItems

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
        fields = ['size','price','slug']

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
    
class CartSerializer(serializers.ModelSerializer):
    cart_total = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    del_address = serializers.SerializerMethodField()
    cart_items = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['slug','cart_total','user','cart_items','del_address']

    def get_cart_total(self,obj):
        return obj.get_cart_total()
    
    def get_user(self,obj):
        return obj.user.email
    
    def get_del_address(self,obj):
        return obj.user.address_set.first().address_text
    
    def get_cart_items(self,obj):
        cart_items = obj.cart_items.all()
        return CartItemsSerializer(cart_items,many=True).data
    

class CartItemsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    cake_name = serializers.SerializerMethodField()
    cake_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItems
        fields = ['cake_name','cake_price','size','quantity','image_url']

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.cake.image:
            return request.build_absolute_uri(obj.cake.image.url)
        return None
    
    def get_cake_name(self,obj):
        return obj.cake.name
    
    def get_cake_price(self,obj):
        return obj.get_item_price()