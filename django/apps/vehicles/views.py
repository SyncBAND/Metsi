from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.db.models import Q

from rest_framework import generics, status, viewsets, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.utils.permissions import IsOwnerProfileOrReadOnly

from .models import Vehicle
from .serializers import VehicleSerializer

from rest_framework.exceptions import PermissionDenied
import json


class VehiclePagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

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

class VehicleViewSet(viewsets.ModelViewSet):

    model = Vehicle
    queryset = Vehicle.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    serializer_class = VehicleSerializer
    pagination_class = VehiclePagination
    paginate_by = 20

    def get_queryset(self):
        
        q = self.request.GET.get('term', '')#.capitalize()
        
        search_qs = Vehicle.objects.filter(Q(name__icontains=q) | Q(trim__make__name__icontains=q) | Q(trim__body_type__name__icontains=q) | Q(trim__transmission__name__icontains=q) | Q(trim__year__icontains=q))
        
        return search_qs
