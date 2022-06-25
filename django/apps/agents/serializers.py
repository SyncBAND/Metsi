from rest_framework import serializers, fields

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError

from .models import Agent, AgentSkills


class AgentSkillsSerializer(serializers.ModelSerializer):

    selected_skills = serializers.SerializerMethodField()
    preselected_skills = serializers.SerializerMethodField()

    class Meta:
        model = AgentSkills
        fields = ('id', 'title', 'selected_skills', 'preselected_skills')
    
    def create(self, validated_data):
        if not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Not permitted')
        
        return AgentSkills.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Not permitted')
        
        return instance.save()

    def get_selected_skills(self, obj):
        if 'skills' in self.context:
            return self.context['skills']
        return []

    def get_preselected_skills(self, obj):
        if 'preselected_skills' in self.context:
            return self.context['preselected_skills']
        return []


class AgentSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    profile_pic = serializers.SerializerMethodField()

    email = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()

    user_id = serializers.SerializerMethodField()

    ratings_for = serializers.SerializerMethodField()
    ratings_from = serializers.SerializerMethodField()

    is_email_verified = serializers.SerializerMethodField()
    date_email_verified = serializers.SerializerMethodField()

    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ('id', 'user_id', 'active', 'title', 'agent', 'email', 'user_name', 'ratings_for', 'ratings_from', 'profile_pic', 'is_email_verified', 'date_email_verified', 'date_joined')

    def get_user_name(self, obj):
        return obj.agent.user.get_full_name()

    def get_user_id(self, obj):
        return obj.agent.user.id

    def get_email(self, obj):
        return obj.agent.user.email

    def get_date_joined(self, obj):
        return obj.agent.user.date_joined

    def get_title(self, obj):
        return 'Agent'

    def get_ratings_from(self, obj):
        if obj:
            return {'total_sum':obj.total_sum_of_ratings_from_endusers, 'total_number':obj.total_number_of_ratings_from_endusers }
        return {'total_sum': 0, 'total_number': 0 }

    def get_ratings_for(self, obj):
        if obj:
            return {'total_sum':obj.total_sum_of_ratings_for_endusers, 'total_number':obj.total_number_of_ratings_for_endusers }
        return {'total_sum': 0, 'total_number': 0 }
        
    def get_is_email_verified(self, obj):
        return obj.agent.user.is_email_verified

    def get_date_email_verified(self, obj):
        return obj.agent.date_email_verified

    def get_profile_pic(self, obj):
        if obj.agent.user.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.agent.user.avatar.url)
                
        return 'https://cdn1.iconfinder.com/data/icons/construction-tool-line-foreman-equipment/512/Wrench-512.png'