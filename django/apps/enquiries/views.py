from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.measure import D
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied

from .models import Enquiry, EnquiryActivity
from .serializers import EnquirySerializer, EnquiryActivitySerializer
from apps.chat.models import Chat, ChatList
from apps.chat.serializers import ChatListSerializer
from apps.endusers.models import Enduser
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile
from apps.utils.notifications import email_notifier
from apps.api_messages.models import Message, MessageTasks

from push_sdk.service import generic_send_push
from push_sdk.tasks import generic_resend_for_push

from datetime import timedelta
import ast
import json


class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'paginator': {'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
                'count': self.page.paginator.count,
                'page_number': self.page.number,
                'num_pages': self.page.paginator.num_pages,
            },
            'results': data
        })
 

class EnquiryViewSet(viewsets.ModelViewSet):

    model = Enquiry
    serializer_class = EnquirySerializer
    pagination_class = Pagination

    authentication_classes = [SessionAuthentication]
    permission_classes      = [AllowAny]
    
    def list(self, request):

        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.user.is_superuser:
            queryset = Enquiry.objects.all()
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Approved)

                skills = request.GET.get('agent', '[]')
                skills = ast.literal_eval(skills)
                if len(skills) > 0:
                    queryset = queryset.filter(skill_needed__in=skills)

                try:
                    location = request.GET.get('location', None)
                    distance = request.GET.get('distance', None)

                    # https://stackoverflow.com/questions/24194710/geodjango-dwithin-errors-when-using-django-contrib-gis-measure-d#answer-24218109
                    if location:
                        # queryset = queryset.filter( destination__distance_lte=(location, D(km=int(distance))) )
                        queryset = queryset.filter( destination__dwithin=(location, float(int(distance) * (1/111.325))) )

                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Approved, mode=mode)
            
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(position__icontains=search) | Q(area__icontains=search) |  Q(severity__icontains=search) |  Q(description__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
            
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        request = self.request
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.is_superuser:
            queryset = Enquiry.objects.all()
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Approved, agent=request.user).order_by('-modified')

                skills = request.GET.get('agent', '[]')
                skills = ast.literal_eval(skills)
                if len(skills) > 0:
                    queryset = queryset.filter(skill_needed__in=skills)

                try:
                    location = request.GET.get('location', None)
                    distance = request.GET.get('distance', None)

                    # https://stackoverflow.com/questions/24194710/geodjango-dwithin-errors-when-using-django-contrib-gis-measure-d#answer-24218109
                    if location:
                        # queryset = queryset.filter( destination__distance_lte=(location, D(km=int(distance))) )
                        queryset = queryset.filter( destination__dwithin=(location, float(int(distance) * (1/111.325))) )

                except Exception as e:
                    pass
                
            else:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Approved, user=request.user, mode=mode).order_by('-modified')

        return queryset
        
    def get_authenticators(self):
        
        self.authentication_classes = [SessionAuthentication]
        if self.request.method == "GET" or self.request.method == "POST":
            if not self.request.GET.get('no_auth', False):
                self.authentication_classes.append(JWTAuthentication)
        return super(EnquiryViewSet, self).get_authenticators()
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def pending(self, request):
        # superuser, endusers 
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Pending).order_by('-modified')
        else:
            queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Pending, user=request.user, mode=mode).order_by('-modified')

        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def approved(self, request):
        # superuser, endusers 
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = Enquiry.objects.filter(Q(status=Enquiry.STATUS_TYPE.Approved) | Q(status=Enquiry.STATUS_TYPE.Reserved) | Q(status=Enquiry.STATUS_TYPE.Referred)).order_by('-modified')
        else:
            queryset = Enquiry.objects.filter(user=request.user, mode=mode).filter(Q(status=Enquiry.STATUS_TYPE.Approved) | Q(status=Enquiry.STATUS_TYPE.Reserved) | Q(status=Enquiry.STATUS_TYPE.Referred)).order_by('-modified')
           
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
                 
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def reserved(self, request):
        # superuser, endusers 
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Reserved).order_by('-modified')
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Reserved, agent=request.user).order_by('-modified')
            else:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Reserved, user=request.user, mode=mode).order_by('-modified')
           
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
                 
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def referred(self, request):
        # superuser, endusers  and agents
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Referred).order_by('-modified')
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Referred, user=request.user).order_by('-modified')
            else:
                queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Referred, enquiry__user=request.user, mode=mode).order_by('-modified')
               
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
             
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EnquiryActivitySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = EnquiryActivitySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def cancelled(self, request):
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Cancelled).order_by('-modified')
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Cancelled, user=request.user).order_by('-modified')
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = EnquiryActivitySerializer(page, many=True, context={'request': request})
                    return self.get_paginated_response(serializer.data)

                serializer = EnquiryActivitySerializer(queryset, many=True, context={'request': request})
                return Response(serializer.data)
            else:
                queryset = Enquiry.objects.filter(status=Enquiry.STATUS_TYPE.Cancelled, user=request.user, mode=mode).order_by('-modified')
              
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
              
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def resolved(self, request):
        try:
            mode = Enquiry._mode_choices[request.GET.get('mode').upper()]
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Resolved).order_by('-modified')
        else:
            if mode == Enquiry.MODE_TYPE.AGENT:
                queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Resolved, user=request.user).order_by('-modified')
            else:
                queryset = EnquiryActivity.objects.filter(status=EnquiryActivity.STATUS.Resolved, enquiry__user=request.user).order_by('-modified')
             
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(vehicle__name__icontains=search) | Q(vehicle__sub_name__icontains=search) | Q(vehicle__trim__make__name__icontains=search) | Q(vehicle__trim__body_type__name__icontains=search) | Q(vehicle__trim__transmission__name__icontains=search) | Q(vehicle__trim__year__icontains=search) | Q(reference__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
               
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EnquiryActivitySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = EnquiryActivitySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


    # Chats: 
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def chatlist(self, request):

        id = request.GET.get('id', 0)
        mode = request.GET.get('mode', '').upper()

        queryset = []
        try:
            
            content_type = ContentType.objects.get_for_model(Enquiry)
            if request.user.is_superuser or mode == 'AGENT':

                if request.user.is_superuser:
                    queryset = ChatList.objects.filter(content_type=content_type, object_id=id).order_by('-modified')
                    
                else:
                    queryset = ChatList.objects.filter(content_type=content_type, object_id=id, respondent=request.user).order_by('-modified')
                    
                    with transaction.atomic():
                        if not queryset.exists():
                            
                            try:
                                enquiry = Enquiry.objects.get(id=id)
                                chatlist = enquiry.chat.create(creator=enquiry.user, respondent=request.user, last_message_sent_by=request.user.id, last_message="Hi. My name is, "+str(request.user.first_name)+". I'll be your assistant.", creator_unread=1)
                                Chat.objects.create(chat_list=chatlist, mode=Enquiry.MODE_TYPE.AGENT, message="Hi. My name is, "+str(request.user.first_name)+". I'll be your assistant.")
                                queryset = [chatlist]
                            except Exception as e:
                                print(e)

            else:
                queryset = ChatList.objects.filter(content_type=content_type, object_id=id, creator=request.user).order_by('-modified')
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ChatListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ChatListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        

class EnquiryActivityViewSet(viewsets.ModelViewSet):

    model = EnquiryActivity
    serializer_class = EnquiryActivitySerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    
    def list(self, request):

        enquiry_id = request.GET.get('enquiry_id', request.data.get('enquiry_id'))

        if request.user.is_superuser:
            queryset = EnquiryActivity.objects.all()
        else:
            queryset = EnquiryActivity.objects.filter(user=request.user)
        
        if enquiry_id:
            queryset = queryset.filter(enquiry_id=enquiry_id)

        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(previous_status_details__icontains=search) | Q(status_details__icontains=search) | Q(location__icontains=search) | Q(problem__icontains=search))
               
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)

