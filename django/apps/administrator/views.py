from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, QueryDict
from django.contrib.auth import logout

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from apps.agents.models import Agent
from apps.endusers.models import Enduser
from apps.enquiries.models import Enquiry
from apps.support.models import Support


''' 
Redirect from email after clicking on new email link
'''     

class Landing(TemplateView):

    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            if request.user.is_superuser:
                return HttpResponseRedirect('/api/administrator/')
            else:
                #return HttpResponseRedirect('http://localhost:8100')
                return HttpResponseRedirect('http://app.metsiapp.co.za/')
            
        return super(Landing, self).dispatch(request, *args, **kwargs)


''' 
Redirect from email after clicking on new email link
'''     

class AdminViewSet(TemplateView):

    template_name = "admin.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            if not request.user.is_superuser: 
                logout(request)
                #return HttpResponseRedirect('http://localhost:8100')
                return HttpResponseRedirect('http://app.metsiapp.co.za/')
        else:
            #return HttpResponseRedirect('http://localhost:8100')
            return HttpResponseRedirect('http://app.metsiapp.co.za/')
            
        return super(AdminViewSet, self).dispatch(request, *args, **kwargs)
    

class AdminDashboardViewSet(generics.GenericAPIView):

    permission_classes = (IsAuthenticated, )
    
    def get(self, request):

        agents = Agent.objects.filter(active=True).count()
        try:
            endusers = Enduser.objects.filter().count()
        except Exception as e:
            print(e)
            endusers = 0
        enquiries = Enquiry.objects.filter().count()
        support = Support.objects.filter().count()

        context = {
            'agents': agents,
            'endusers': endusers,
            'enquiries': enquiries,
            'support': support,
        }
        return Response(context)

    def post(self, request):
        return
        