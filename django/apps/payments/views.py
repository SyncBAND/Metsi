from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.exceptions import PermissionDenied

from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
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
 

class InvoiceViewSet(viewsets.ModelViewSet):

    model = Invoice
    serializer_class = InvoiceSerializer
    pagination_class = Pagination

    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    
    def list(self, request):

        if request.user.is_superuser:
            queryset = Invoice.objects.all()
        else:
            queryset = Invoice.objects.filter(invoiced_by__user=request.user)
    
        page = self.paginate_queryset(queryset.only('id').order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.only('id').order_by('-modified'), many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def active(self, request):
        # superuser, endusers
        if request.user.is_superuser:
            queryset = Invoice.objects.get(status=Invoice.STATUS_TYPE.Active).only('id').order_by('-modified')
        else:
            queryset = Invoice.objects.filter(status=Invoice.STATUS_TYPE.Active, invoiced_to__user=request.user).only('id').order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def cancelled(self, request):

        mode = request.GET.get('mode', 0)

        if request.user.is_superuser:
            queryset = Invoice.objects.get(status=Invoice.STATUS_TYPE.Cancelled).only('id').order_by('-modified')
        else:
            queryset = Invoice.objects.filter(status=Invoice.STATUS_TYPE.Cancelled, invoiced_to__user=request.user).only('id').order_by('-modified')
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def paid(self, request):

        mode = request.GET.get('mode', 0)

        if request.user.is_superuser:
            queryset = Invoice.objects.get(status=Invoice.STATUS_TYPE.Paid).only('id').order_by('-modified')
        else:
            queryset = Invoice.objects.filter(status=Invoice.STATUS_TYPE.Paid, invoiced_to__user=request.user).only('id').order_by('-modified')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class PaymentViewSet(viewsets.ModelViewSet):

    model = Payment
    serializer_class = PaymentSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    
    def list(self, request):

        enquiry_id = request.GET.get('enquiry_id', request.data.get('enquiry_id', 0))

        if request.user.is_superuser:
            queryset = Payment.objects.all()
        else:
            queryset = Payment.objects.filter(invoiced_by__user=request.user)
    
        page = self.paginate_queryset(queryset.only('id').order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.only('id').order_by('-modified'), many=True)
        return Response(serializer.data)

