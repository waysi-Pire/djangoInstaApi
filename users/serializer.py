from rest_framework import serializers
from django.contrib.auth.models import User,update_last_login
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import ast

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','password']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200, write_only=True)
    access_token  = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username,password=password)
        if user is None:
            raise serializers.ValidationError(detail="A User with username and password is not found")
        try:
            refresh_token = RefreshToken.for_user(user)
            access_token= refresh_token.access_token
            update_last_login(None,user)
            return {
                "user_id":user.id,
                "access_token":str(access_token),
                "refresh_token":str(refresh_token)
            }
        except User.DoesNotExist:
            raise serializers.ValidationError("A User with provided username does not exist.")
        
        










    


