from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializer import UserSerializer,LoginSerializer
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated




@api_view(['POST'])
def signupView(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        obj = serializer.save()
        obj.set_password(request.data.get('password'))
        obj.save()
        return JsonResponse(serializer.data,status=200)
    return JsonResponse(serializer.errors,status=400)

@api_view(['POST'])
def signinView(request):
    serializer = LoginSerializer(data=request.data)
    res = {}
    if serializer.is_valid():
        res = {"msg":"login successfully","data":serializer.validated_data}
        return JsonResponse(res)
    else:
        return JsonResponse(serializer.errors)

