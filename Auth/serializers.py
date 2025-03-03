from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['name','email','slug','image_url']

    def get_name(self,obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_image_url(self,obj):
        request = self.context.get('request')
        if obj.user_image:
            return request.build_absolute_uri(obj.user_image.url)
        return None
