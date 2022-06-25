from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Enduser, EnduserRatings, EnduserRatingsHistory
from .serializers import EnduserSerializer
from apps.agents.models import Agent
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

        
class EnduserViewSet(viewsets.ModelViewSet):

    model = Enduser
    serializer_class = EnduserSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination

    def list(self, request):

        if request.user.is_superuser:
            queryset = Enduser.objects.all()
        else:
            queryset = Enduser.objects.filter(enduser__user=request.user)
            
        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(enduser__user__first_name__icontains=search) | Q(enduser__user__last_name__icontains=search) | Q(enduser__user__email__icontains=search) )
               
        try:
            page = self.paginate_queryset(queryset.order_by('-modified'))
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({})

    def get_queryset(self):
        
        if self.request.user.is_superuser:
            qt = Enduser.objects.all().order_by('-modified')
            return qt
        else:
            return Enduser.objects.filter(enduser__user=self.request.user).order_by('-modified')

        return Enduser.objects.none()
    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def rate(self, request):
        
        try:
            rating = request.data.get('rating', None)
            review = request.data.get('review', '')
            mode = request.data.get('mode', '')
            content_type = request.data.get('content_type', '')
            object_id = request.data.get('object_id', '')
            enduser_id = request.data.get('enduser_id', 0)

            content_type = ContentType.objects.get(model=content_type)
            object_type = content_type.get_object_for_this_type(id=object_id)

            if not rating:
                return Response({'detail': 'Rating was not given'}, status=status.HTTP_400_BAD_REQUEST)
            
            rating = int(rating)

            with transaction.atomic():

                # agent rates endusers
                if mode == 'AGENT':

                    enduser_being_rated = Enduser.objects.select_related().get(enduser__user = object_type.user)

                    user_profile_making_rating = UserProfile.objects.select_related().get(user = request.user)

                    try:
                        agent = Agent.objects.select_related().get(agent = user_profile_making_rating)
                    except Exception as e:
                        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    
                    try:
                        enduser_ratings = EnduserRatings.objects.get(user_profile_making_rating=user_profile_making_rating, enduser_being_rated=enduser_being_rated)
                        
                        EnduserRatingsHistory.objects.create(enduser_ratings=enduser_ratings, previous_rating=enduser_ratings.rating, previous_review=enduser_ratings.review)
                        
                        # if editting, minus previous rating and add new one
                        # enduser rating FROM agent
                        enduser_being_rated.total_sum_of_ratings_from_agents = enduser_being_rated.total_sum_of_ratings_from_agents - enduser_ratings.rating + rating
                        enduser_being_rated.save()

                        # agent rating AN enduser
                        agent.total_sum_of_ratings_for_endusers = agent.total_sum_of_ratings_for_endusers - enduser_ratings.rating + rating
                        agent.save()

                        enduser_ratings.review = review
                        enduser_ratings.rating = rating
                        enduser_ratings.editted = True
                        enduser_ratings.save()

                    except:

                        EnduserRatings.objects.create(user_profile_making_rating=user_profile_making_rating, enduser_being_rated=enduser_being_rated, review=review, rating=rating, content_type=content_type, object_id=object_id)
                        
                        # enduser rating FROM agent
                        enduser_being_rated.total_sum_of_ratings_from_agents = enduser_being_rated.total_sum_of_ratings_from_agents + rating
                        enduser_being_rated.total_number_of_ratings_from_agents = enduser_being_rated.total_number_of_ratings_from_agents + 1
                        enduser_being_rated.save()

                        # agent rating AN enduser
                        agent.total_sum_of_ratings_for_endusers = agent.total_sum_of_ratings_for_endusers + rating
                        agent.total_number_of_ratings_for_endusers = agent.total_number_of_ratings_for_endusers + 1
                        agent.save()
                    
                    object_type.rating_by_agent = rating
                    object_type.save()
                    
                    return Response({'detail': 'Rated'}, status=status.HTTP_200_OK)
                
                return Response({'detail': 'Agent rates users'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)