from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name','email','slug']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise  serializers.ValidationError("User with this email does not exist")

        user = authenticate(email=user.email,password=password) 
        if user:
            data["user"] = user 
            return data
        raise serializers.ValidationError({"password":"Incorrect email or password"})        
              