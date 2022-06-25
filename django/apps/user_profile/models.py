from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator

from collections import namedtuple

class UserMode(CreatedModifiedMixin):

    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class UserProfile(CreatedModifiedMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    _mode_choices = {
        'ENDUSER': 0,
        'AGENT': 1,
        'ADMIN': 2
    }
    mode_choices = (
        'ENDUSER',
        'AGENT',
        'ADMIN'
    )
    MODE_TYPE = namedtuple('MODE_TYPE', mode_choices)(*range(0, len(mode_choices)))
    mode = models.PositiveIntegerField(default=0, choices=get_field_choices(MODE_TYPE))

    share_code = models.CharField(max_length=128)

    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    verified_email = models.BooleanField(default=False)
    date_email_verified = models.DateTimeField(default=timezone.now)

    verified_cell = models.BooleanField(default=False)

    id_number = models.CharField(max_length=7, null=True, blank=True)
    api_key = models.CharField(max_length=32, null=True, blank=True)

    gender_choices = (
        'Male',
        'Female',
        'Other',
    )
    GENDER_TYPE = namedtuple('GENDER_TYPE', gender_choices)(*range(0, len(gender_choices)))
    gender = models.PositiveIntegerField(default=0, choices=get_field_choices(GENDER_TYPE))

    id_copy = models.FileField(blank=True, null=True, upload_to="user/documents/id_copy/")
    id_copy_extra = models.FileField(blank=True, null=True, upload_to="user/documents/id_copy/")

    document_cv = models.FileField(blank=True, null=True, upload_to="user/documents/cv/")
    document_extra = models.FileField(blank=True, null=True, upload_to="user/documents/extra/")

    
    def save(self, *args, **kwargs):
        if not self.share_code:
            while True:
                share_code = random_generator(length=6, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(share_code=share_code).only('share_code').exists():
                    break
            self.share_code = share_code

        if not self.api_key:
            while True:
                api_key = random_generator(length=32, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(share_code=api_key).only('api_key').exists():
                    break
            self.api_key = api_key

        return super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.first_name

    @classmethod
    def get_queryset(cls, user):

        if not user.is_authenticated:
            return UserProfile.objects.none()
        
        if user.is_superuser or user.is_staff:
            return UserProfile.objects.all()
        
        return UserProfile.objects.filter(user=user)


class UserSessions(CreatedModifiedMixin):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)

    ip_address = models.CharField(max_length=128, null=True, blank=True)

    mode_choices = (
        'ENDUSER',
        'AGENT',
        'ADMIN'
    )
    MODE_TYPE = namedtuple('MODE_TYPE', mode_choices)(*range(0, len(mode_choices)))
    mode = models.PositiveIntegerField(default=0, choices=get_field_choices(MODE_TYPE))

    # update later - keep track of time
    session_code = models.CharField(max_length=128, null=True, blank=True)

    logs = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.profile.user.first_name


class UserChanges(CreatedModifiedMixin):

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    previous_id_copy = models.FileField(blank=True, null=True, upload_to="agents/documents/id_copy/")
    previous_id_copy_extra = models.FileField(blank=True, null=True, upload_to="agents/documents/id_copy/")

    def __str__(self):
        return self.profile.user.first_name