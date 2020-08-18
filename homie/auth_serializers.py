from rest_framework import serializers, validators,exceptions,status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings

import json,re,logging
import datetime

from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.validators import ASCIIUsernameValidator

logger = logging.getLogger('django')

class RegSerializer(serializers.ModelSerializer):
    mobileno = serializers.CharField(source='username')

    class Meta:
        model = AuthUser
        error_messages = {"mobileno": {"required": "Please enter a valid mobile number"}}
        fields = ['first_name','email','password','mobileno']

    def validate_mobileno(self,mobileno):
        user = AuthUser.objects.filter(username=mobileno).first()
        
        if user:
            pass
            #raise serializers.ValidationError("mobileno already exists")

        Pattern = re.compile("^[0-9]*$")
        # Pattern = re.compile("^(\+){1}[0-9]*$") 
        
        if Pattern.match(mobileno):
            return mobileno
        
        else:
            logger.info('invalid')
            raise serializers.ValidationError("invalid mobile number")

class MultiFieldJWTSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }

        user =  AuthUser.objects.filter(username=attrs.get("username")).first()
        print(user)
        if user:
            credentials['username'] = user.username
            print(credentials)
        reply = {}


        try:
            data = super().validate(credentials)
            print(json.dumps(data))
            reply['status'] = "SUCCESS"
            data['user'] = str(user.id)
            reply['data'] = data
        
        except Exception as ex:
            reply['status'] = "ERROR"
            reply['message'] = str(ex)
            print(str(ex))
            reply['error_code'] = "AUTH_ERROR"


        return reply



class OtpLoginSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        user =  AuthUser.objects.filter(username=attrs.get("username")).first()
        reply = {}

        if user:
            try:
                data = {}
                refresh = self.get_token(user)
                data['refresh'] = str(refresh)
                data['expiry'] = (refresh.lifetime + refresh.current_time).timestamp()
                data['access'] = str(refresh.access_token)
                data['user'] = str(user.id)
                reply['status'] = "SUCCESS"
                reply['data'] = data
            
            except Exception as ex:
                reply['status'] = "ERROR"
                reply['message'] = str(ex)
                reply['error_code'] = "AUTH_ERROR"
        
        else:
            reply['status'] = "ERROR"
            reply['message'] = "User "+attrs.get("username")+" not found"
            reply['error_code'] = "AUTH_ERROR"
        return reply

    
class CustomRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token)}
        data['expiry'] = (refresh.lifetime + refresh.current_time).timestamp()

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)
        return data