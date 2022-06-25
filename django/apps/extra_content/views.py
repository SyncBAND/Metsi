from django.utils import timezone
from django.db import transaction

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied

from .models import ExtraContent, ExtraContentActivity, ExtraContentRatings, ExtraContentRatingsHistory
from .serializers import ExtraContentSerializer
from apps.user_profile.models import UserProfile
from apps.utils.permissions import IsOwnerProfileOrReadOnly

class Pagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 10

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

class ExtraContentViewSet(viewsets.ModelViewSet):

    model = ExtraContent
    serializer_class = ExtraContentSerializer
    pagination_class = Pagination

    authentication_classes = [SessionAuthentication]
    permission_classes = (AllowAny, )

    def list(self, request):

        if request.user.is_superuser:
            queryset = ExtraContent.objects.filter()
        else:
            queryset = ExtraContent.objects.filter(status = ExtraContent.STATUS_TYPE.Active, start_date__lte=timezone.localtime(timezone.now()), expiry_date__gte=timezone.localtime(timezone.now()))
    
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)

    def get_queryset(self):

        if self.request.user.is_superuser:
            queryset = ExtraContent.objects.filter()
        else:
            queryset = ExtraContent.objects.filter(status = ExtraContent.STATUS_TYPE.Active, start_date__lte=timezone.localtime(timezone.now()), expiry_date__gte=timezone.localtime(timezone.now()))
    
        return queryset.order_by('-modified')

    def get_authenticators(self):
        
        self.authentication_classes = [SessionAuthentication]
        if self.request.method == "GET" or self.request.method == "POST":
            if not self.request.GET.get('no_auth', False):
                self.authentication_classes.append(JWTAuthentication)
        return super(ExtraContentViewSet, self).get_authenticators()

    @decorators.action(detail=False, methods=['get'])
    def tutorials(self, request):

        queryset = ExtraContent.objects.filter(status = ExtraContent.STATUS_TYPE.Active, extra_content_type=ExtraContent.TYPE.Tutorial, start_date__lte=timezone.localtime(timezone.now()), expiry_date__gte=timezone.localtime(timezone.now())).order_by('-modified')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    @decorators.action(detail=True, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def interact(self, request, pk=0):
        
        try:
            
            with transaction.atomic():
                extra_content = ExtraContent.objects.select_related().get(pk = pk, status = ExtraContent.STATUS_TYPE.Active, start_date__lte=timezone.localtime(timezone.now()), expiry_date__gte=timezone.localtime(timezone.now()))
                
                try:
                    ExtraContentActivity.objects.filter(user=request.user, extra_content=extra_content)
                except:
                    extra_content.url_interactions = extra_content.url_interactions + 1
                    extra_content.save()

                    ExtraContentActivity.objects.create(user=request.user, extra_content=extra_content)
                
                return Response({'detail': 'Updated'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=True, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def rate(self, request, pk=0):
        
        try:
            rating = request.data.get('rating', None)
            review = request.data.get('review', '')
            
            if not rating:
                return Response({'detail': 'Rating was not given'}, status=status.HTTP_400_BAD_REQUEST)

            rating = int(rating)
            
            with transaction.atomic():

                extra_content_being_rated = ExtraContent.objects.select_related().get(pk = pk)

                user_profile_making_rating = UserProfile.objects.select_related().get(user = request.user)
                
                try:
                    extra_content_ratings = ExtraContentRatings.objects.get(user_profile_making_rating=user_profile_making_rating, extra_content_being_rated=extra_content_being_rated)
                    
                    ExtraContentRatingsHistory.objects.create(extra_content_ratings=extra_content_ratings, previous_rating=extra_content_ratings.rating, previous_review=extra_content_ratings.review)
                    
                    # if editting, minus previous rating and add new one
                    # to get rating percentage = (extra_content_being_rated.total_sum_of_ratings/5)/extra_content_being_rated.total_number_of_ratings
                    extra_content_being_rated.total_sum_of_ratings = extra_content_being_rated.total_sum_of_ratings - extra_content_ratings.rating + rating
                    extra_content_being_rated.save()

                    extra_content_ratings.review = review
                    extra_content_ratings.rating = rating
                    extra_content_ratings.editted = True
                    extra_content_ratings.save()

                except:

                    ExtraContentRatings.objects.create(user_profile_making_rating=user_profile_making_rating, extra_content_being_rated=extra_content_being_rated, review=review, rating=rating)
                    
                    # to get rating percentage = (extra_content_being_rated.total_sum_of_ratings/5)/extra_content_being_rated.total_number_of_ratings
                    extra_content_being_rated.total_sum_of_ratings = extra_content_being_rated.total_sum_of_ratings + rating
                    extra_content_being_rated.total_number_of_ratings = extra_content_being_rated.total_number_of_ratings + 1
                    extra_content_being_rated.save()
                
                return Response({'detail': 'Rated'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)