from rest_framework import serializers, fields

from versatileimagefield.serializers import VersatileImageFieldSerializer

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

import datetime
import ast
import json

from apps.agents.models import Agent, AgentChanges, AgentSkills
from apps.api_messages.models import Message
from apps.chat.models import Chat, ChatList
from apps.endusers.models import Enduser
from .models import Enquiry, EnquiryActivity
from apps.user_profile.models import UserProfile
from apps.utils.notifications import email_notifier

from push_sdk.service import generic_send_push


class EnquirySerializer(serializers.ModelSerializer):
    
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

    name = serializers.SerializerMethodField()

    enduser_name = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()

    mode = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    current_status = serializers.SerializerMethodField()
    current_mode = serializers.SerializerMethodField()

    skill = serializers.SerializerMethodField()

    interest = serializers.SerializerMethodField()

    distance = serializers.SerializerMethodField()

    ref = serializers.SerializerMethodField()

    enquiry_created = serializers.SerializerMethodField()

    enquiry_id_num = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = ('id', 'enquiry_id_num', 'name', 'enduser_name', 'agent_name', 'severity', 'area', 'ref', 'enquiry_created', 'skill', 'distance', 'interest', 'position', 'description', 'problem', 'user', 'mode', 'status', 'status_details', 'latitude', 'longitude', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'images', 'current_status', 'current_mode', 'created', 'modified', 'rating_by_user', 'rating_by_agent', 'destination', 'location', 'suburb', 'city', 'province', 'country')


    def create(self, validated_data):
        
        try:
            with transaction.atomic():
                user = self.context['request'].user
                if user.is_authenticated:
                    validated_data['user'] = user

                    mode = self.context['request'].data.get('mode').upper()
                    
                    validated_data['mode'] = Enquiry._mode_choices[mode]
                    
                    enduser = Enduser.objects.select_related().get(enduser__user_id=user.id)
                    enduser.pending = models.F('pending') + 1
                    enduser.save()

                    skill_needed = self.context['request'].data.get('skills_needed', 'Contractor')
                    
                    validated_data['skill_needed'] = AgentSkills.objects.get(title=skill_needed)

                    enquiry = Enquiry.objects.create(**validated_data)

                    details = 'Description: ' + str(enquiry.description) + \
                        '\nProblem: ' + str(enquiry.problem) + \
                        '\nSeverity: ' + str(enquiry.severity) + \
                        '\nArea: ' + str(enquiry.area) + \
                        '\nPosition: ' + str(enquiry.position) + \
                        '\nLocation: ' + str(enquiry.location) + \
                        '\nCreated' + str(enquiry.created) + "\n\n"
                    
                    message = "Hi " + user.first_name + ", \n\n This is to inform you about the enquiry you have logded with the following details - \n\n" + details + "Regards,\n\nTake care"

                    email_notifier.delay(user.id, get_current_site(self.context['request']).domain, origin="apps.enquiries.serializers.EnquirySerializer", message=message, subject='Enquiry for {}'.format(enquiry.problem), email_to=[user.email, 'yung.twala@gmail.com'])

                    return enquiry
                else:
                    raise ValidationError('Action not permitted')

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
                        raise ValidationError('User not permitted')
                else:
                    raise ValidationError('Action not permitted')

        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return instance

    def get_ref(self, obj):
        if obj.reference:
            return obj.reference
        return ''

    def get_name(self, obj):
        return "{}, {}".format(obj.problem, obj.severity)

    def get_current_mode(self, obj):
        return Enquiry.mode_choices[obj.mode]
    
    def get_current_status(self, obj):
        return Enquiry.status_choices[obj.status]

    def get_mode(self, obj):
        return Enquiry.mode_choices[obj.mode]
    
    def get_enquiry_created(self, obj):
        return obj.created

    def get_skill(self, obj):
        return obj.skill_needed.title

    def get_enquiry_id_num(self, obj):
        return obj.id

    def get_interest(self, obj):
        return False
    
    def get_distance(self, obj):
        if 'distance' in self.context['request'].GET:
            # https://stackoverflow.com/questions/24194710/geodjango-dwithin-errors-when-using-django-contrib-gis-measure-d#answer-24218109
            return obj.destination.distance( GEOSGeometry(self.context['request'].GET.get('location')) ) * 111.325
        return 0

    def get_agent_name(self, obj):
        if obj.agent:
            return obj.agent.first_name
        return ''

    def get_enduser_name(self, obj):
        return obj.user.first_name

    def get_images(self, obj):
        
        image_list = []

        if obj.image_1:
            request = self.context.get('request')
            if request:
                image_list.append(str(request.build_absolute_uri(obj.image_1.url)))

        if obj.image_2:
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


class EnquiryActivitySerializer(serializers.ModelSerializer):

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

    name = serializers.SerializerMethodField()
    problem = serializers.SerializerMethodField()
    skill = serializers.SerializerMethodField()

    enduser_name = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()

    user_name = serializers.SerializerMethodField()
    
    mode = serializers.SerializerMethodField()
    
    images = serializers.SerializerMethodField()

    previous_status_ = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()

    description = serializers.SerializerMethodField()

    enquiry_created = serializers.SerializerMethodField()

    ref = serializers.SerializerMethodField()

    enquiry_id_num = serializers.SerializerMethodField()
    
    previous_enquiry_update = serializers.SerializerMethodField()
    
    rating_by_user = serializers.SerializerMethodField()
    
    rating_by_agent = serializers.SerializerMethodField()
    
    interest = serializers.SerializerMethodField()
    
    class Meta:
        model = EnquiryActivity
        fields = ('id', 'enquiry_id', 'user_name', 'enduser_name', 'agent_name', 'mode', 'enquiry_id_num', 'ref', 'interest', 'rating_by_user', 'rating_by_agent', 'user', 'name', 'description', 'severity', 'problem', 'skill', 'area', 'position', 'current_status', 'previous_status', 'previous_status_', 'previous_status_details', 'previous_skill_needed', 'skill_needed', 'status', 'status_details', 'latitude', 'longitude', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6', 'image_7', 'image_8', 'images', 'enquiry_created', 'created', 'modified', 'destination', 'previous_enquiry_update', 'location', 'city', 'province', 'country')

    def create(self, validated_data):

        try:

            with transaction.atomic():

                request = self.context['request']
                user = request.user
                body = self.context['request']
                data = request.data

                enquiry_id = request.data.get('enquiry_id', 0)
                enquiry = Enquiry.objects.select_related().get(id=enquiry_id)
                
                status = EnquiryActivity._status_choices[data['current_status']]

                validated_data['user'] = user
                validated_data['status'] = status
                validated_data['previous_status'] = enquiry.status
                validated_data['previous_status_details'] = enquiry.status_details
                validated_data['previous_skill_needed'] = enquiry.skill_needed
                validated_data['previous_update'] = enquiry.modified

                _mode = self.context['request'].data.get('mode').upper()
                mode = EnquiryActivity._mode_choices[_mode]
                
                validated_data['mode'] = mode

                if mode == EnquiryActivity.MODE_TYPE.AGENT:
                    # agent
                    agent = Agent.objects.select_related().get(agent__user_id=user.id)
                    enduser = Enduser.objects.select_related().get(enduser__user_id=enquiry.user.id)

                    if enquiry.agent:
                        if enquiry.agent != request.user:
                            return ValidationError('Enquiry is {} by another agent.'.format(data['current_status']))

                else:
                    enduser = Enduser.objects.select_related().get(enduser__user_id=enquiry.user.id)
                    agent = None
                
                
                if enquiry.status == int(status):
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Enquiry is already {}'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'], Enquiry.STATUS_TYPE[status])
                    enquiry.save()
                    raise ValidationError('Enquiry is already ' + str(Enquiry.STATUS_TYPE[status]) + '. Nothing to be done.')
            
                elif enquiry.status == Enquiry.STATUS_TYPE.Cancelled:
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Enquiry is cancelled'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                    enquiry.save()
                    raise ValidationError('Enquiry is cancelled. Nothing to be done.')

                if enquiry.status == Enquiry.STATUS_TYPE.Pending:
                    enduser.pending = models.F('pending') - 1
                    if status == Enquiry.STATUS_TYPE.Approved or status == Enquiry.STATUS_TYPE.Referred or status == Enquiry.STATUS_TYPE.Reserved:
                        enduser.approved = models.F('approved') + 1


                if status == Enquiry.STATUS_TYPE.Approved:

                    if request.user.is_superuser:

                        validated_data['destination'] = enquiry.destination
                        validated_data['city'] = enquiry.city
                        validated_data['country'] = enquiry.country
                        validated_data['location'] = enquiry.location
                        validated_data['suburb'] = enquiry.suburb
                        validated_data['province'] = enquiry.province
                        validated_data['latitude'] = enquiry.latitude
                        validated_data['longitude'] = enquiry.longitude

                        subject = "{}. Your enquiry was approved".format(enquiry.reference)
                        origin = "apps.enquiries.serializers.EnquiryActivitySerializer.create"
                    
                        message = "Admin approved your enquiry - Ref: {}".format(enquiry.reference)

                        email_message = "Hi " + enquiry.user.first_name + ", \n\n Enquiry ref:" + str(enquiry.reference) + " was approved.\n\nRegards,\n\nTake care"

                        email_notifier.delay(request.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[request.user.email])

                        email_notifier.delay(enquiry.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.user.email])

                        enquiry.admin = request.user
                        enquiry.status = Enquiry.STATUS_TYPE.Approved
                        enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Approved'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])

                    else:

                        enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Not permitted to approve'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                        enquiry.save()
                        raise ValidationError('Not permitted.')

                elif status == Enquiry.STATUS_TYPE.Reserved:
                    
                    if enquiry.user == agent.agent.user:
                        enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Enquiry is cancelled'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                        enquiry.save()
                        raise ValidationError('You cannot reserve your own enquiry.')
                    elif enquiry.agent is not None:
                        enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Enquiry is already reserved'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                        enquiry.save()
                        raise ValidationError('Enquiry is already reserved.')

                    agent.reserved = models.F('reserved') + 1
                    enquiry.agent = agent.agent.user
                    enquiry.status = status
                    
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Reserved'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                    
                    subject = "{}. Enquiry was reserved - {}".format(enquiry.reference, agent.agent.user.id)
                    origin = "apps.enquiries.serializers.EnquiryActivitySerializer.create"

                    email_message = "Hi " + agent.agent.user.first_name + ", \n\n Enquiry ref:" + str(enquiry.reference) + " was reserved.\n\nRegards,\n\nTake care"

                    email_notifier.delay(agent.agent.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[agent.agent.user.email])

                    email_notifier.delay(enquiry.admin.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])

                elif status == Enquiry.STATUS_TYPE.Referred:
                    # only agents and seuperusers can refer
                    enquiry.status = Enquiry.STATUS_TYPE.Approved
                    # superuser can also refer
                    
                    print(validated_data)
                    
                    if agent:
                        agent.reserved = models.F('reserved') - 1
                        agent.referred = models.F('referred') + 1

                        enquiry.position = validated_data['position']
                        enquiry.area = validated_data['area']
                        enquiry.severity = validated_data['severity']
                        enquiry.skill_needed = AgentSkills.objects.get(title=validated_data['skill_needed']) 

                    else:
                        agent = Agent.objects.select_related().get(agent__user_id=enquiry.agent.id)
                        agent.reserved = models.F('reserved') - 1
                        agent.reserved = models.F('referred') + 1
                        agent.save()

                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Referred'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])
                    
                    validated_data['destination'] = enquiry.destination
                    validated_data['city'] = enquiry.city
                    validated_data['country'] = enquiry.country
                    validated_data['location'] = enquiry.location
                    validated_data['suburb'] = enquiry.suburb
                    validated_data['province'] = enquiry.province
                    validated_data['latitude'] = enquiry.latitude
                    validated_data['longitude'] = enquiry.longitude

                    subject = "{}. Enquiry was referred - {}".format(enquiry.reference, agent.agent.user.id)
                    origin = "apps.enquiries.serializers.EnquiryActivitySerializer.create"

                    email_message = "Hi " + agent.agent.user.first_name + ", \n\n Enquiry ref:" + str(enquiry.reference) + " was referred.\n\nRegards,\n\nTake care"

                    email_notifier.delay(enquiry.agent.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[agent.agent.user.email])

                    email_notifier.delay(enquiry.admin.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])

                    enquiry.agent = None

                elif status == Enquiry.STATUS_TYPE.Cancelled:
                    

                    subject = "{}. Enquiry was canceled - {}".format(enquiry.reference, request.user.id)
                    origin = "apps.enquiries.serializers.EnquiryActivitySerializer.create"

                    email_message = "Hi, \n\n Enquiry ref:" + str(enquiry.reference) + " was canceled.\n\nRegards,\n\nTake care"

                    if agent or user.is_superuser:
                        
                        if enquiry.status == Enquiry.STATUS_TYPE.Reserved:

                            if user.is_superuser:
                                agent = Agent.objects.select_related().get(agent__user_id=enquiry.agent.id) 

                            enquiry.agent = None

                            agent.reserved = models.F('reserved') - 1
                            agent.cancelled = models.F('cancelled') + 1

                            validated_data['status'] = EnquiryActivity.STATUS.Approved
                            validated_data['status_details'] = "Cancelled: " + str(validated_data['status_details'])

                            enquiry.status = Enquiry.STATUS_TYPE.Approved
                            
                            email_notifier.delay(agent.agent.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[agent.agent.user.email])

                            email_notifier.delay(enquiry.admin.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])
                        
                        elif enquiry.status == Enquiry.STATUS_TYPE.Approved:

                            enquiry.agent = None

                            enduser.approved = models.F('approved') - 1
                            enduser.pending = models.F('cancelled') + 1

                            validated_data['status'] = EnquiryActivity.STATUS.Cancelled
                            validated_data['status_details'] = "Cancelled: " + str(validated_data['status_details'])

                            enquiry.status = Enquiry.STATUS_TYPE.Cancelled

                            email_notifier.delay(enquiry.admin.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])

                        else:
                            
                            if not user.is_superuser:
                                enquiry.agent = agent.agent.user
                                agent.cancelled = models.F('cancelled') + 1
                                
                            enquiry.status = status
                            enduser.cancelled = models.F('cancelled') + 1

                            email_notifier.delay(enquiry.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.user.email])
                            
                    elif not user.is_superuser:

                        enquiry.status = status
                        enduser.cancelled = models.F('cancelled') + 1
                    
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Cancelled'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])

                    validated_data['destination'] = enquiry.destination
                    validated_data['city'] = enquiry.city
                    validated_data['country'] = enquiry.country
                    validated_data['location'] = enquiry.location
                    validated_data['suburb'] = enquiry.suburb
                    validated_data['province'] = enquiry.province
                    validated_data['latitude'] = enquiry.latitude
                    validated_data['longitude'] = enquiry.longitude

                elif status == Enquiry.STATUS_TYPE.Resolved:
                    # checks how far the agent is. accepts if less than 1km away
                    # if enquiry.destination.distance( GEOSGeometry(validated_data['destination']) ) * 111.325 > 1:
                    #     print(enquiry.destination.distance( GEOSGeometry(validated_data['destination']) ) * 111.325)
                    #     raise ValidationError('You are too far from destination')

                    enduser.resolved = models.F('resolved') + 1
                    enduser.approved = models.F('approved') - 1
                    
                    agent.resolved = models.F('resolved') + 1
                    agent.reserved = models.F('reserved') - 1

                    enquiry.agent = agent.agent.user
                    enquiry.status = status

                    validated_data['city'] = enquiry.city
                    validated_data['country'] = enquiry.country
                    validated_data['location'] = enquiry.location
                    validated_data['suburb'] = enquiry.suburb
                    validated_data['province'] = enquiry.province
                    
                    # https://stackoverflow.com/questions/24194710/geodjango-dwithin-errors-when-using-django-contrib-gis-measure-d#answer-24218109
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Resolved {:.2f}km away from the original location entry'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'], round(enquiry.destination.distance( GEOSGeometry(validated_data['destination']) ) * 111.325, 2) )

                    subject = "{}. Enquiry was resolved - {}".format(enquiry.reference, agent.agent.user.id)
                    origin = "apps.enquiries.serializers.EnquiryActivitySerializer.create"

                    email_message = "Hi, \n\n Enquiry ref:" + str(enquiry.reference) + " was resolved.\n\nRegards,\n\nTake care"

                    email_notifier.delay(enquiry.agent.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[agent.agent.user.email])

                    email_notifier.delay(enquiry.admin.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])

                    email_notifier.delay(enquiry.user.id, get_current_site(request).domain, origin=origin, message=email_message, subject=subject, email_to=[enquiry.admin.email])

                elif user.is_superuser and status == Enquiry.STATUS_TYPE.Reopened:
                    enquiry.agent = None
                    enquiry.status = Enquiry.STATUS_TYPE.Approved
                    # check if enquiry was cancelled or resolved and minus one
                
                    enquiry.logs = '\n\n{} Mode: {}, User: {} - {} -> Reopened'.format(timezone.localtime(timezone.now()), _mode, user.id, validated_data['status_details'])

                if agent:
                    agent.save()
                if enduser:
                    enduser.save()

                # old images should come last
                if enquiry.image_1:
                    validated_data['image_5'] = enquiry.image_1
                if enquiry.image_2:
                    validated_data['image_6'] = enquiry.image_2
                if enquiry.image_3:
                    validated_data['image_7'] = enquiry.image_3
                if enquiry.image_4:
                    validated_data['image_8'] = enquiry.image_4
                
                # save new images at the end of the enquiry
                if 'image_1' in validated_data:
                    enquiry.image_5 = validated_data['image_1']
                if 'image_2' in validated_data:
                    enquiry.image_6 = validated_data['image_2']
                if 'image_3' in validated_data:
                    enquiry.image_7 = validated_data['image_3']
                if 'image_4' in validated_data:
                    enquiry.image_8 = validated_data['image_4']
                
                enquiry.status_details = validated_data['status_details']

                enquiry.save()

                validated_data['enquiry'] = enquiry
                return  EnquiryActivity.objects.create(**validated_data)

        except Exception as e:
            raise serializers.ValidationError(str(e))

        return

    def update(self, instance, validated_data):
        return

    def get_agent_name(self, obj):
        if obj.enquiry.agent:
            return obj.enquiry.agent.first_name
        return ''

    def get_enduser_name(self, obj):
        return obj.enquiry.user.first_name

    def get_user_name(self, obj):
        return obj.user.first_name

    def get_enquiry_id_num(self, obj):
        return obj.enquiry.id

    def get_ref(self, obj):
        if obj.enquiry.reference:
            return obj.enquiry.reference
        return ''

    def get_mode(self, obj):
        return EnquiryActivity.mode_choices[obj.mode]
    
    def get_name(self, obj):
        return "{}, {}".format(obj.enquiry.problem, obj.enquiry.severity)
    
    def get_description(self, obj):
        return obj.enquiry.description
    
    def get_problem(self, obj):
        return obj.enquiry.problem
    
    def get_enquiry_created(self, obj):
        return obj.enquiry.created

    def get_skill(self, obj):
        if obj.skill_needed:
            return obj.skill_needed.title
        return 'Contractor'

    def get_previous_status_(self, obj):
        return EnquiryActivity.previous_status_choices[obj.previous_status]
    
    def get_current_status(self, obj):
        return EnquiryActivity.status_choices[obj.status]
    
    def get_previous_enquiry_update(self, obj):
        return obj.previous_update

    def get_interest(self, obj):
        return ''

    def get_rating_by_agent(self, obj):
        return obj.enquiry.rating_by_agent

    def get_rating_by_user(self, obj):
        return obj.enquiry.rating_by_user

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