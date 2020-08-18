from django.shortcuts import render
from django.contrib.auth.models import User as AuthUser
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.response import Response
import logging, json
import homie.auth_serializers as homie_ser
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated,AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    ser = homie_ser.RegSerializer(data=request.data)
    reply = {}
    mobNum = request.POST.get("mobileno")

    if not ser.is_valid():
        for err in ser.errors:
            #   if err=='mobileno':
            #         continue
            reply['message'] = ser.errors[err][0]
            reply['status'] = "ERROR"
            reply['error_code'] = "INVALID_"+err.upper()
            dict_obj = json.dumps(reply)
            return HttpResponse(dict_obj, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = AuthUser.objects.filter(username=mobNum).first()
        if user is None:
            user = ser.save()
            user.set_password(user.password)
            user.save()
        else:
            reply['status'] = "ERROR"
            reply['message'] = "Phone number already Registered"
            dict_obj = json.dumps(reply)
            return HttpResponse(json.dumps(reply), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        print(str(e))
        reply['status'] = "ERROR"
        reply['message'] = "Server: User not created. Please contact support or retry."
        dict_obj = json.dumps(reply)
        return HttpResponse(json.dumps(reply), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    reply['status'] = "SUCCESS"
    reply['message'] = "Signup was sucessful"
    dict_obj = json.dumps(reply)
    return HttpResponse(dict_obj, status=status.HTTP_201_CREATED)