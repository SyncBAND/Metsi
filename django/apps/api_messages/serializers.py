from rest_framework import serializers, fields

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Message


class MessageSerializer(serializers.ModelSerializer):

    m_type = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'user', 'subject', 'message', 'recipients', 'origin', 'remote_id', 'remote_message_status', 'resend_counter', 'logs', 'status', 'current_status', 'type', 'm_type')
    
    def create(self, validate_data):

        user = self.context['request'].user
        
        return Message.objects.create(**validate_data)
    
    def update(self, instance, validated_data):
        return 

    def get_m_type(self, obj):

        return Message._type[obj.type]
    
    def get_current_status(self, obj):

        return Message.status_choices[obj.status]