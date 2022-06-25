from rest_framework import serializers, fields

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError

from .models import ExtraContent, ExtraContentActivity
from apps.endusers.models import Enduser
from apps.utils.notifications import email_notifier


class ExtraContentSerializer(serializers.ModelSerializer):

    image_1 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_2 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_3 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_4 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    image_5 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_6 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_7 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    image_8 = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )

    images = serializers.SerializerMethodField()
    current_extra_content_type = serializers.SerializerMethodField()

    class Meta:
        model = ExtraContent
        fields = ('id', 'title', 'extra_content_type', 'start_date', 'url_interactions', 'url', 'seen', 'expiry_date', 'description', 'status', 'latitude', 'longitude', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'images', 'created', 'modified', 'current_extra_content_type', 'location', 'suburb', 'city', 'province', 'country')

    def get_current_extra_content_type(self, obj):
        return ExtraContent.extra_content_choices[obj.extra_content_type]

    def create(self, validated_data):
        
        try:

            with transaction.atomic():
                user = self.context['request'].user

                if user.is_authenticated:

                    mode = self.context['request'].data.get('mode').upper()
                    
                    extra_content_type = self.context['request'].data.get('extra_content_type').upper()

                    extra_content = ExtraContent.objects.create(**validated_data)

                    if extra_content_type == ExtraContent.TYPE.Advert:

                        enduser = Enduser.objects.get(enduser__user_id=user.id)
                        enduser.adverts = enduser.adverts + 1
                        enduser.save()

                        details = 'Title: ' + str(extra_content.title) + \
                            '\nDescription: ' + str(extra_content.description) + \
                            '\nUrl: ' + str(extra_content.url) + \
                            '\nLocation: ' + str(extra_content.location) + \
                            '\nStart: ' + str(extra_content.start_date) + \
                            '\nExpire: ' + str(extra_content.expiry_date) + \
                            '\nCreated' + str(extra_content.created) + "\n\n"

                        message = "Hi " + user.first_name + ", \n\n This is to inform you about your new Advert with the following details - \n\n" + details + "Regards,\n\nTake care"

                        email_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.extra_content.serializers.ExtraContentSerializer", message=message, subject='New Advert {}, was uploaded'.format(extra_content.title), email_to=[user.email, 'yung.twala@gmail.com'])

                    return extra_content

                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return

    def update(self, instance, validated_data):
        
        try:
            with transaction.atomic():

                if self.context['request'].user.is_authenticated:
                    if self.context['request'].user == instance.user or self.context['request'].user.is_superuser:
                        instance.save()
                    else:
                        raise serializers.ValidationError('User not permitted')
                else:
                    raise serializers.ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance
      
    def get_images(self, obj):
        
        image_list = []

        if obj.image_1:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_1.url)))

        if obj.image_2:
            print(self.context)
            request = self.context['request']
            if request:
                
                image_list.append(str(request.build_absolute_uri(obj.image_2.url)))

        if obj.image_3:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_3.url)))

        if obj.image_4:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_4.url)))

        if obj.image_5:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_5.url)))

        if obj.image_6:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_6.url)))

        if obj.image_7:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_7.url)))

        if obj.image_8:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_8.url)))

        return image_list


class ExtraContentActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ExtraContentActivity
        fields = ('id', 'title')
        