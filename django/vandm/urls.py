"""login_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework import routers

from apps.user_profile.api import ChangePasswordViewSet, UserProfileViewSet, UpdateUserEmailViewSet
from apps.api_auth.views import LogoutView, LogoutAllView
from apps.administrator import views as administrator_views
from apps.chat import views as chat_views
from apps.support import views as support_views
from apps.enquiries import views as enquiry_views
from apps.agents import views as agent_views
from apps.payments import views as payment_views
from apps.vehicles.views import VehicleViewSet
from apps.agents.views import AgentViewSet
from apps.endusers.views import EnduserViewSet
from apps.extra_content.views import ExtraContentViewSet
from apps.api_messages.views import MessageViewSet
from push_sdk.views import PushDeviceViewSet


api_router = routers.DefaultRouter()
api_router.register(r'support', support_views.SupportViewSet, basename='support')
api_router.register(r'support-activity', support_views.SupportActivityViewSet, basename='support_activity')
api_router.register(r'invoices', payment_views.InvoiceViewSet, basename='invoices')
api_router.register(r'enquiries', enquiry_views.EnquiryViewSet, basename='enquiries')
api_router.register(r'enquiries-activity', enquiry_views.EnquiryActivityViewSet, basename='enquiries_activity')
api_router.register(r'extra-content', ExtraContentViewSet, basename='extra_content')
api_router.register(r'chat', chat_views.ChatViewSet, basename='chat')
api_router.register(r'chat-list', chat_views.ChatListViewSet, basename='chatlist')
api_router.register(r'logout', LogoutView, basename='logout')
api_router.register(r'logout-all', LogoutAllView, basename='logout_all')
api_router.register(r'user-profile', UserProfileViewSet, basename='user_profile')
api_router.register(r'update-profile', UserProfileViewSet, basename='update_profile')
api_router.register(r'agent-skills', agent_views.AgentSkillsViewSet, basename='agent_skills')
api_router.register(r'vehicle', VehicleViewSet, basename='vehicle')
api_router.register(r'agent', AgentViewSet, basename='agent')
api_router.register(r'enduser', EnduserViewSet, basename='enduser')
api_router.register(r'register-device', PushDeviceViewSet, basename='register_device')
api_router.register(r'message-recieved', MessageViewSet, basename='message_recieved')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/auth/', include('apps.api_auth.urls')),
    url(r'^api/administrator/', include('apps.administrator.urls')),
    url(r'^api/update-profile-email/(?P<pk>\d+)/$', UpdateUserEmailViewSet.as_view(), name='update_profile_email'),
    url(r'^api/update-user-password/(?P<pk>\d+)/$', ChangePasswordViewSet.as_view(), name='update_password'),
    url(r'^api/', include(api_router.urls)),
    url(r'^$', administrator_views.Landing.as_view(), name='landing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)