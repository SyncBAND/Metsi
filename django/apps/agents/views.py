from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import generics, status, viewsets, pagination, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied

from .models import Agent, AgentRatings, AgentRatingsHistory, AgentSkills
from .serializers import AgentSerializer, AgentSkillsSerializer
from apps.endusers.models import Enduser
from apps.enquiries.models import Enquiry
from apps.user_profile.models import UserProfile
from apps.utils.permissions import IsOwnerProfileOrReadOnly
from apps.utils.notifications import email_notifier
import ast


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

        
class AgentSkillsViewSet(viewsets.ModelViewSet):

    model = AgentSkills
    serializer_class = AgentSkillsSerializer
    queryset = AgentSkills.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = (AllowAny, )

    def get_serializer_context(self):
        context = super(AgentSkillsViewSet, self).get_serializer_context()

        agent_id = self.request.GET.get('agent_id', None)
        try:
            agent = Agent.objects.select_related().get(agent__user__id=agent_id)
            context.update( {'preselected_skills': [{obj.id: obj.title} for obj in agent.skills.select_related().all()]} )
            context.update( {'skills': ['{}: {}'.format(obj.id, obj.title) for obj in agent.skills.select_related().all()]} )
        except:
            context.update( {'preselected_skills': []} )
            context.update( {'skills': []} )

        return context

class AgentViewSet(viewsets.ModelViewSet):

    model = Agent
    serializer_class = AgentSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly)
    pagination_class = Pagination

    def list(self, request):

        if request.user.is_superuser:
            queryset = Agent.objects.all().order_by('-modified')
        else:
            queryset = Agent.objects.filter(agent__user=self.request.user).order_by('-modified')

        search = request.GET.get('search', None)
        if search:
            queryset = queryset.filter(Q(agent__user__first_name__icontains=search) | Q(agent__user__last_name__icontains=search) | Q(agent__user__email__icontains=search) )
               
        page = self.paginate_queryset(queryset.order_by('-modified'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.order_by('-modified'), many=True)
        return Response(serializer.data)
        
    def get_queryset(self):
        
        if self.request.user.is_superuser:
            return Agent.objects.all().order_by('-modified')
        else:
            return Agent.objects.filter(agent__user=self.request.user).order_by('-modified')

        return Agent.objects.none()
    

    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def get_activation_key(self, request):

        try:
            skills = request.data.get('agent', '[]')

            user = UserProfile.objects.select_related().get(user = request.user)

            try:
                agent = Agent.objects.select_related().get(agent=user)
                skills = ast.literal_eval(skills)
                agent.skills.clear()
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            except Agent.DoesNotExist:
                agent = Agent.objects.create(agent=user)
                skills = ast.literal_eval(skills)
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            # can check for cv or other qualifications before sending pin
            #if agent.document_cv:

            if user.verified_email:
                
                if agent.active:
                    message = "Hi " + user.user.first_name + ", \n\n Please find your agent activation key below. \n\n" + agent.agent_key + "\n\nUse it on the app and keep it safe. \n\nRegards,\n\nTake care"
                    
                    email_notifier.delay(user.user.id, get_current_site(request).domain, origin="apps.agent.views.AgentViewSet.get_activation_pin", message=message, subject='Agent activation pin', email_to=[user.user.email])

                    return Response({'success': True, 'email': True, 'detail': "Email with your pin was sent."}, status=status.HTTP_200_OK)

                else:
                    return Response({'success': True, 'email': True, 'detail': "Awaiting activation from administrator"}, status=status.HTTP_200_OK)
                    
            else:
                return Response({'success': False, 'email': False, 'detail': "Please verify your email to reserve"}, status=status.HTTP_200_OK)

                # return Response({'success': False, 'detail': "Please submit your CV"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # used by admin
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def activate_agent(self, request):

        try:
            
            if not request.user.is_superuser:
                return Response({'detail': 'Not permitted'}, status=status.HTTP_401_UNAUTHORIZED)

            else:
                user = get_user_model().objects.get(id=request.data['user_id'])

                agent = Agent.objects.get(agent__user=user)
                agent.active = True
                agent.save()

                message = "Hi {}, \n\nYour Agent account has been activated. You can go on the app to do more.\n\nRegards".format(user.first_name)

                email_notifier.delay(user.id, get_current_site(request).domain, origin="apps.agents.views.AgentViewsSet.activate_agent", message=message, subject="Agent account activated", email_to=[user.email])

                serializer = AgentSerializer([agent], many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def activate(self, request):

        try:

            pin = request.data.get('pin', None)
            enquiry_id = request.data.get('enquiry_id', 0)
            skills = request.data.get('agent', '[]')

            user = UserProfile.objects.select_related().get(user = request.user)

            try:
                agent = Agent.objects.select_related().get(agent=user)
                skills = ast.literal_eval(skills)
                agent.skills.clear()
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            except Agent.DoesNotExist:
                agent = Agent.objects.create(agent=user)
                skills = ast.literal_eval(skills)
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            # can check for cv or other qualifications before activating
            #if agent.document_cv:

            if user.verified_email:
                if agent.agent_key == pin:
                    agent.active = True
                    agent.save()
                    return Response({'success': True, 'email': True, 'detail': "Pin is correct."}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'email': True, 'detail': "Incorrect pin"}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'email': False, 'detail': "Please verify your email"}, status=status.HTTP_200_OK)

                # return Response({'success': False, 'detail': "Please submit your CV"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=False, methods=['get'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def is_active(self, request):

        try:
            skills = request.data.get('agent', '[]')

            user = UserProfile.objects.select_related().get(user = request.user)

            try:
                agent = Agent.objects.select_related().get(agent=user)
                skills = ast.literal_eval(skills)
                agent.skills.clear()
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            except Agent.DoesNotExist:
                agent = Agent.objects.create(agent=user)
                skills = ast.literal_eval(skills)
                for skill in skills:
                    agent.skills.add(skill)
                agent.save()

            if user.verified_email:
                
                if agent.active:

                    return Response({'success': True, 'detail': ""}, status=status.HTTP_200_OK)

                else:
                    return Response({'success': False, 'detail': "Awaiting administrator to activate your account"}, status=status.HTTP_200_OK)
                    
            else:
                return Response({'success': False, 'email': False, 'detail': "Please verify your email to reserve"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    @decorators.action(detail=False, methods=['post'], permission_classes = (IsAuthenticated, IsOwnerProfileOrReadOnly))
    def rate(self, request):
        
        # try:
        rating = request.data.get('rating', None)
        review = request.data.get('review', '')
        mode = request.data.get('mode', '')
        content_type = request.data.get('content_type', '')
        object_id = request.data.get('object_id', '')
        
        content_type = ContentType.objects.get(model=content_type)
        object_type = content_type.get_object_for_this_type(id=object_id)

        if not rating:
            return Response({'detail': 'Rating was not given'}, status=status.HTTP_400_BAD_REQUEST)

        rating = int(rating)

        with transaction.atomic():
            
            if mode == 'ENDUSER':

                agent_being_rated = Agent.objects.select_related().get(agent__user = object_type.agent)
                user_profile_making_rating = UserProfile.objects.select_related().get(user = request.user)

                try:
                    enduser = Enduser.objects.select_related().get(enduser = user_profile_making_rating)
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    
                try:
                    agent_ratings = AgentRatings.objects.get(user_profile_making_rating=user_profile_making_rating, agent_being_rated=agent_being_rated)
                    
                    AgentRatingsHistory.objects.create(agent_ratings=agent_ratings, previous_rating=agent_ratings.rating, previous_review=agent_ratings.review)
                    
                    # if editting, minus previous rating and add new one
                    # agent rating FROM enduser
                    agent_being_rated.total_sum_of_ratings_from_endusers = agent_being_rated.total_sum_of_ratings_from_endusers - agent_ratings.rating + rating
                    agent_being_rated.save()

                    # enduser rating an agent
                    enduser.total_sum_of_ratings_for_agents = enduser.total_sum_of_ratings_for_agents - agent_being_rated.rating + rating
                    enduser.save()

                    agent_ratings.review = review
                    agent_ratings.rating = rating
                    agent_ratings.editted = True
                    agent_ratings.save()

                except:
                    
                    AgentRatings.objects.create(user_profile_making_rating=user_profile_making_rating, agent_being_rated=agent_being_rated, review=review, rating=rating, content_type=content_type, object_id=object_id)
                    
                    # to get rating percentage = (agent_being_rated.total_sum_of_ratings_from_endusers/5)/agent_being_rated.total_number_of_ratings_from_endusers
                    agent_being_rated.total_sum_of_ratings_from_endusers = agent_being_rated.total_sum_of_ratings_from_endusers + rating
                    agent_being_rated.total_number_of_ratings_from_endusers = agent_being_rated.total_number_of_ratings_from_endusers + 1
                    agent_being_rated.save()
                
                    # enduser rating an agent
                    enduser.total_sum_of_ratings_for_agents = enduser.total_sum_of_ratings_for_agents + rating
                    enduser.total_number_of_ratings_for_agents = enduser.total_number_of_ratings_for_agents + 1
                    enduser.save()

                object_type.rating_by_user = rating
                object_type.save()

                return Response({'detail': 'Rated'}, status=status.HTTP_200_OK)

            return Response({'detail': 'User rates agents'}, status=status.HTTP_400_BAD_REQUEST)

        # except Exception as e:
        #     return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

