from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q, Sum
from django.contrib.contenttypes.models import ContentType

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.exceptions import PermissionDenied

from .models import Chat, ChatList
from .serializers import ChatSerializer, ChatListSerializer
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.user_profile.models import UserProfile

from django.db import transaction
from django.contrib.auth import get_user_model

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


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


class ChatListViewSet(viewsets.ModelViewSet):

    model = ChatList
    serializer_class = ChatListSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination
    
    def list(self, request):
        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        id = self.request.GET.get('id', '0')
        model = self.request.GET.get('model', 'Enquiry')

        if self.request.user.is_superuser:
            return ChatList.objects.filter(id=id).order_by('-modified')
        else:
            # currently not in use - refer to models using Chatlst as GenericRelation
            mode = self.request.GET.get('mode', '').upper()
            if mode == 'AGENT':
                return ChatList.objects.filter(id=id, respondent_id=self.request.user.id, active_respondent=True).order_by('-modified')
            else:
                return ChatList.objects.filter(id=id, creator_id=self.request.user.id, active_creator=True).order_by('-modified')
                
        return []

    @decorators.action(detail=False, methods=['put'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def delete(self, request):

        id = request.data.get('id', 0)
        mode = request.data.get('mode', '').upper()
        
        if self.request.user.is_superuser:
            ChatList.objects.filter(id=id).update(status=ChatList.TYPE.Deleted)
        else:
            if mode == 'AGENT':
                return ChatList.objects.filter(id=id, respondent_id=request.user.id, active_respondent=True).update(active_respondent=False)
            else:
                return ChatList.objects.filter(id=id, creator_id=request.user.id, active_creator=True).update(active_creator=False)

        return Response({'detail': 'Chat deleted'}, status=status.HTTP_200_OK)


class ChatViewSet(viewsets.ModelViewSet):

    model = Chat
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination
    
    def list(self, request):
        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):

        chat_list_id = self.request.GET.get('chat_list_id', 0)

        if self.request.user.is_superuser:
            return Chat.objects.filter(chat_list_id=chat_list_id).order_by('-modified')
        else:
            mode = self.request.GET.get('mode', '').upper()
            if mode == 'AGENT':
                return Chat.objects.filter(chat_list_id=chat_list_id, chat_list__respondent_id=self.request.user.id, active_respondent=True).order_by('-modified')
            else:
                return Chat.objects.filter(chat_list_id=chat_list_id, chat_list__creator_id=self.request.user.id, active_creator=True).order_by('-modified')
                
        return []

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def chats(self, request):

        # fix in future not to pull everything - but to paginate

        if request.user.is_superuser:
            chat_list_id = self.request.GET.get('id', 0)
            queryset = Chat.objects.filter(chat_list_id=chat_list_id).order_by('-modified') 
        else:
            return Response({'detail': 'Not permitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @decorators.action(detail=False, methods=['put'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def delete(self, request):

        id = request.data.get('id', 0)
        mode = request.data.get('mode', '').upper()
        
        if self.request.user.is_superuser:
            Chat.objects.filter(id=id)
        else:
            if mode == 'AGENT':
                return Chat.objects.filter(id=id, chat_list__respondent_id=request.user.id, active_respondent=True).update(active_respondent=False)
            else:
                return Chat.objects.filter(id=id, chat_list__creator_id=request.user.id, active_creator=True).update(active_creator=False)

        return Response({'detail': 'Message deleted'}, status=status.HTTP_200_OK)

