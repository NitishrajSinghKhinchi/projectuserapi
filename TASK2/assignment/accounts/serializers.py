from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import CustomUser

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('name','email','date_of_birth','password')
        write_only_fields = ('password')
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            date_of_birth=validated_data['date_of_birth'],
            password=validated_data['password']
        )
        # print(validated_data['name'])
        # print(validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('name','email','date_of_birth')
        