from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError

from .models import Enduser

class EnduserSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    profile_pic = serializers.SerializerMethodField()

    email = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()

    ratings_for = serializers.SerializerMethodField()
    ratings_from = serializers.SerializerMethodField()

    active = serializers.SerializerMethodField()
    is_email_verified = serializers.SerializerMethodField()
    date_email_verified = serializers.SerializerMethodField()

    user_id = serializers.SerializerMethodField()

    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = Enduser
        fields = ('id', 'user_id', 'title', 'active', 'enduser', 'email', 'user_name', 'ratings_for', 'ratings_from', 'profile_pic', 'is_email_verified', 'date_email_verified', 'date_joined')

    def get_user_name(self, obj):
        return obj.enduser.user.get_full_name()

    def get_user_id(self, obj):
        return obj.enduser.user.id

    def get_email(self, obj):
        return obj.enduser.user.email

    def get_date_joined(self, obj):
        return obj.enduser.user.date_joined

    def get_active(self, obj):
        return obj.enduser.verified_email

    def get_is_email_verified(self, obj):
        return obj.enduser.verified_email

    def get_date_email_verified(self, obj):
        return obj.enduser.date_email_verified

    def get_title(self, obj):
        return 'Enduser'

    def get_ratings_from(self, obj):
        if obj:
            return {'total_sum':obj.total_sum_of_ratings_from_agents, 'total_number':obj.total_number_of_ratings_from_agents }
        return {'total_sum': 0, 'total_number': 0 }
    
    def get_ratings_for(self, obj):
        if obj:
            return {'total_sum':obj.total_sum_of_ratings_for_agents, 'total_number':obj.total_number_of_ratings_for_agents }
        return {'total_sum': 0, 'total_number': 0 }

    def get_profile_pic(self, obj):
        if obj.enduser.user.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.enduser.user.avatar.url)

        return 'https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-alt-512.png'
