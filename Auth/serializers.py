from rest_framework import serializers
from .models import CustomUser,Address, DeliveryPerson
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['name','email','slug','image_url','role']

    def get_name(self,obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.user_image:
            return request.build_absolute_uri(obj.user_image.url)
        return None

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_text', 'longitude', 'latitude', 'slug']

class FullUserDetailsSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source='address_set',many=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','slug','image_url','address','phone_no']

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.user_image and hasattr(obj.user_image, 'url'):
            return request.build_absolute_uri(obj.user_image.url)
        return None

class DeliveryPersonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    phone_no = serializers.SerializerMethodField()
    class Meta:
        model = DeliveryPerson
        fields = ['name','vehicle_number','slug','phone_no']
    
    def get_name(self,obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_phone_no(self,obj):
        return obj.user.phone_no