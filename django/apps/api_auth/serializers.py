from django.contrib.auth import get_user_model, login
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site

from apps.utils.notifications import mail_notifier
from apps.user_profile.models import UserProfile, UserSessions
from apps.endusers.models import Enduser
from apps.agents.models import Agent

import ast


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=get_user_model().objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'password', 'password2', 'email', 'first_name', 'group')
        extra_kwargs = {
            'first_name': {'required': True},
            'cell': {'required': True}
        }
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        
        with transaction.atomic():

            try:
                mode = self.context['request'].data.get('mode', 'enduser').upper()

                user = get_user_model().objects.create(
                    cell=validated_data['cell'],
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    is_active=True,
                    group=validated_data['group']
                )

                user.set_password(validated_data['password'])
                user.save()

                profile = UserProfile.objects.create(user=user, mode=UserProfile._mode_choices[mode])
                UserSessions.objects.create(profile=profile, mode=UserProfile._mode_choices[mode])
                
                if mode == 'ENDUSER':
                    Enduser.objects.create(enduser=profile)
                elif mode == 'AGENT':
                    agent = Agent.objects.create(agent=profile)
                    skills = self.context['request'].data.get('agent', '[]')
                    skills = ast.literal_eval(skills)
                    for skill in skills:
                        agent.skills.add(skill)
                    agent.save()

                #celery
                mail_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.api_auth.serializers.RegisterSerializer", verification_type=2, subject='Verifying email address', sign_off='Take care', email_to=validated_data['email'])
                                
                return user

            except Exception as e:
                raise serializers.ValidationError(e)

class RegisterViewSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=get_user_model().objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'password', 'password2', 'email', 'first_name', 'group')
        extra_kwargs = {
            'first_name': {'required': True},
            'cell': {'required': True}
        }
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        
        with transaction.atomic():
            try:
                user = get_user_model().objects.create(
                    cell=validated_data['cell'],
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    is_active=True,
                    group=validated_data['group']
                )

                user.set_password(validated_data['password'])
                user.save()

                #celery
                mail_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.api_auth.serializers.RegisterSerializer", verification_type=2, subject='Verifying email address', sign_off='Take care', email_to=validated_data['email'])
                
                login(self.context['request'], user)

                return user
            except Exception as e:
                raise serializers.ValidationError(e)




class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('cell', 'email', 'first_name')

    def create(self, validated_data):

        print(validated_data)

        return