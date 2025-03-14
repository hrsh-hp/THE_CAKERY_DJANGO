from rest_framework import serializers
from django.db import models

from Auth.serializers import DeliveryPersonSerializer
from cakes.models import Cake, CakeLike, CakeSize, Cart, CartItems, Order, Payment, Review, Topping

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

class ToppingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['name','price','slug']

class CakeFullSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    sizes = SizesSerializer(many=True)
    toppings = ToppingsSerializer(many=True)

    class Meta:
        model = Cake
        fields = ['name','slug','image_url','liked','likes_count','description','available_toppings','sizes','toppings']

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
        fields = ['slug','cart_total','user','del_address','cart_items']

    def get_cart_total(self,obj):
        return obj.get_cart_total()
    
    def get_user(self,obj):
        return obj.user.email
    
    def get_del_address(self,obj):
        return obj.user.address_set.first().address_text
    
    def get_cart_items(self,obj):
        cart_items = obj.cart_items.all()
        return CartItemsSerializer(cart_items,many=True,context={'request':self.context.get('request')}).data
    

class CartItemsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    cake_name = serializers.SerializerMethodField()
    cake_price = serializers.SerializerMethodField()
    # size = SizesSerializer()
    toppings = ToppingsSerializer(many=True)
    size = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItems
        fields = [ 'slug','cake_name','cake_price','size','quantity','toppings','image_url']
    
    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.cake.image and request:
            return request.build_absolute_uri(obj.cake.image.url)
        return None
    
    def get_size(self,obj):
        return obj.size.size

    def get_cake_name(self,obj):
        return obj.cake.name
    
    def get_cake_price(self,obj):
        return obj.get_item_price()
    
class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['payment_method','is_paid','transaction_id']

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    payment = PaymentSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    delivery_person = DeliveryPersonSerializer(read_only=True)
    is_reviewed = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['slug','total_price','del_address','status','items','payment','created_at','delivery_person','is_reviewed']

    def get_items(self, obj):
        return CartItemsSerializer(obj.cart.cart_items.all(), many=True,context={'request':self.context.get('request')}).data
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%b %d, %Y")
    
    def get_is_reviewed(self, obj):
        return hasattr(obj, "review") and obj.review is not None
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating','review_text','slug','tags']