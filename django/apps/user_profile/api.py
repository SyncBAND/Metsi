from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
 
from rest_framework import decorators, generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .serializers import ChangePasswordSerializer, UpdateUserSerializer
from apps.agents.models import Agent
from apps.endusers.models import Enduser
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile
from apps.utils.notifications import mail_notifier, email_update_notifier, email_notifier

from rest_framework.exceptions import PermissionDenied

import ast

class UserProfileViewSet(viewsets.ModelViewSet):

    model = get_user_model()
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return get_user_model().objects.none()
    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def email(self, request):
        
        if request.user.is_superuser:
            try:
                user = get_user_model().objects.get(id=request.data['user_id'])
                
                message = str(request.data['message'])

                email_notifier.delay(user.id, get_current_site(request).domain, origin="apps.user_profile.api.UserProfileViewSet.email", message=message, subject=request.data['subject'], email_to=[user.email])

                return Response({'detail': "Email was sent."}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def stats(self, request):
        # superuser, endusers 
        try:
            mode = UserProfile._mode_choices[request.GET.get('mode').upper()]
            
            user = UserProfile.objects.get(user_id=request.GET['id'])

            with transaction.atomic():
                mode = request.GET.get('mode').upper()
                
                if mode == 'ENDUSER':
                    try:
                        statistics = Enduser.objects.get(enduser=user)
                    except Enduser.DoesNotExist:
                        statistics = Enduser.objects.create(enduser=user)

                elif mode == 'AGENT':
                    try:
                        statistics = Agent.objects.get(agent=user)
                        skills = ast.literal_eval(self.request.GET.get('agent'))
                        statistics.skills.clear()
                        for skill in skills:
                            statistics.skills.add(skill)
                        statistics.save()
                    except Agent.DoesNotExist:
                        statistics = Agent.objects.create(agent=user)
                        skills = ast.literal_eval(self.request.GET.get('agent'))
                        for skill in skills:
                            statistics.skills.add(skill)
                        statistics.save()
                        
                if mode == 'ENDUSER':
                    return Response({'detail': [{'name': 'Pending', 'value':statistics.pending, 'notify': False}, {'name': 'Approved', 'value':statistics.approved, 'notify': False}, {'name': 'Resolved', 'value':statistics.resolved, 'notify': False}, {'name': 'Cancelled', 'value':statistics.cancelled, 'notify': False}]}, status=status.HTTP_200_OK)
                elif mode == 'AGENT':
                    return Response({'detail': [{'name': 'Reserved', 'value':statistics.reserved}, {'name': 'Referred', 'value':statistics.referred}, {'name': 'Resolved', 'value':statistics.resolved}, {'name': 'Cancelled', 'value':statistics.cancelled}]}, status=status.HTTP_200_OK)

            return Response({'detail': []}, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserViewSet(viewsets.ModelViewSet):

    model = get_user_model()
    permission_classes = [IsAuthenticated, IsOwnerProfileOrReadOnly]
    serializer_class = UpdateUserSerializer
    
    def get_queryset(self):
        if 'pk' in self.kwargs:
            return get_user_model().objects.filter(pk=self.kwargs['pk'])
        return get_user_model().objects.none()

class ChangePasswordViewSet(APIView):

    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)

    def patch(self, request, pk=None, *args, **kwargs):

        try:
            with transaction.atomic():
                password = request.data['password']
                password2 = request.data['password2']

                user = get_user_model().objects.get(pk=pk)
                
                if password != password2:
                    return Response({'detail': "Password fields didn't match."}, status=status.HTTP_400_BAD_REQUEST)
                elif len(password) < 5:
                    return Response({'detail': "Password length cannot be less than 5 characters."}, status=status.HTTP_400_BAD_REQUEST)

                profile = UserProfile.objects.get(user=user)

                try:
                    user.set_password(password)
                    user.save()

                    update_session_auth_hash(request, user)  # Important!
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                if user.is_email_verified:
                    email_update_notifier.delay(user.id, subject='Password updated', msg="Your password was updated successfully.", origin='apps.user_profile.api.ChangePasswordViewSet', sign_off='Take care', email_to=user.email)
            
                return Response({'detail': "Your password was updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateUserEmailViewSet(APIView):
    
    permission_classes = [IsAuthenticated, IsOwnerProfileOrReadOnly]

    def patch(self, request, pk=None, *args, **kwargs):
        
        try:
            with transaction.atomic():
                email = request.data['email']

                user = get_user_model().objects.get(pk=pk)
                
                exists = get_user_model().objects.filter(email=email).exclude(id=pk, is_email_verified=False).exists()
                if exists:
                    return Response({'detail': "User with email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                
                profile = UserProfile.objects.get(user=user)

                profile.verified_email = False
                profile.email = email
                profile.save()

                try:
                    mail_notifier.delay(user.id, get_current_site(request).domain, origin="apps.user_profile.api.UpdateUserEmailViewSet", verification_type=2, subject='Verifying email address - Update', sign_off='Take care', email_to=email)
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                return Response({'detail': "Sending mail to your email address"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)