from rest_framework import serializers, fields

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import transaction

import datetime

from .models import Invoice, Payment

class InvoiceSerializer(serializers.ModelSerializer):
    
    current_status = serializers.SerializerMethodField()
    mode =  serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ('id', 'invoiced_by', 'invoiced_to', 'reference', 'amount', 'status', 'mode', 'discount', 'total_amount', 'status_details', 'current_status', 'created', 'modified')


    def create(self, validated_data):
        
        try:
            with transaction.atomic():
                if self.context['request'].user.is_authenticated:
                    return Invoice.objects.create(**validated_data)
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return

    def update(self, instance, validated_data):
        
        try:
            with transaction.atomic():

                if self.context['request'].user.is_authenticated:
                    instance.save()
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance

    
    def get_mode(self, obj):
        return Invoice.mode_choices[obj.mode]
    
    def get_current_status(self, obj):
        return Invoice.status_choices[obj.status]

class PaymentSerializer(serializers.ModelSerializer):

    image_1 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_2 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    images = serializers.SerializerMethodField()

    previous_status_ = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ('id', 'invoice', 'reference', 'total_paid', 'proof_of_payment', 'extra_documents', 'status', 'current_status', 'status_details', 'image_1', 'image_2', 'images', 'created', 'modified')


    def create(self, validated_data):

        try:
            with transaction.atomic():
                if self.context['request'].user.is_authenticated:
                    return Payment.objects.create(**validated_data)
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return

    def update(self, instance, validated_data):
        
        try:
            with transaction.atomic():

                if self.context['request'].user.is_authenticated:
                    instance.save()
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance
    
    def get_current_status(self, obj):
        return Payment.status_choices[obj.status]

    def get_images(self, obj):
        
        image_list = []

        if obj.image_1:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_1.url)))

        if obj.image_2:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_2.url)))

        return image_list