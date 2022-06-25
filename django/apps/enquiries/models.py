from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator
from apps.agents.models import AgentSkills

from versatileimagefield.fields import VersatileImageField, PPOIField

from collections import namedtuple


class Enquiry(CreatedModifiedMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiry_creator")
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiry_agent", null=True, blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiry_admin", null=True, blank=True)
    
    severity = models.CharField(max_length=128, null=False)
    area = models.CharField(max_length=128, null=True, blank=True)
    position = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    problem = models.TextField(null=True, blank=True)
    skill_needed = models.ForeignKey(AgentSkills, on_delete=models.CASCADE)

    rating_by_user = models.PositiveIntegerField(blank=True, null=True)
    rating_by_agent = models.PositiveIntegerField(blank=True, null=True)

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

    status_choices = (
        'Pending',
        'Approved',
        'Cancelled',
        'Reserved',
        'Referred',
        'Resolved',
        'Reopened',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(null=True, blank=True)

    reference = models.CharField(max_length=32, null=False)

    image_1 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    destination = models.PointField(blank=True, null=True)

    city = models.CharField(max_length=128, null=True, blank=True)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)
    
    chat = GenericRelation('chat.ChatList')

    # -------- 

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                reference = random_generator(length=9, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(reference=reference).only('reference').exists():
                    break
            self.reference = reference
        return super(Enquiry, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.id)


class EnquiryActivity(CreatedModifiedMixin):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiry_activity_creator")
    
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE)

    # these usually used for referred/resolved issues 
    severity = models.CharField(max_length=128, null=True, blank=True)
    area = models.CharField(max_length=128, null=True, blank=True)
    position = models.CharField(max_length=128, null=True, blank=True)
    skill_needed = models.ForeignKey(AgentSkills, on_delete=models.CASCADE, null=True, blank=True, related_name="enquiry_activity_skill")

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
    
    _status_choices = {
        'Pending': 0,
        'Approved': 1,
        'Cancelled': 2,
        'Reserved': 3,
        'Referred': 4,
        'Resolved': 5,
        'Reopened': 6,
    }

    previous_status_choices = (
        'Pending',
        'Approved',
        'Cancelled',
        'Reserved',
        'Referred',
        'Resolved',
        'Reopened',
    )
    PREVIOUS_STATUS = namedtuple('PREVIOUS_STATUS', previous_status_choices)(*range(0, len(previous_status_choices)))
    previous_status = models.PositiveIntegerField(default=0, choices=get_field_choices(PREVIOUS_STATUS))

    previous_status_details = models.TextField(null=True, blank=True)
    previous_skill_needed = models.ForeignKey(AgentSkills, on_delete=models.CASCADE, related_name="enquiry_activity_prev_skill")
    
    previous_update = models.DateTimeField(default=timezone.now)

    status_choices = (
        'Pending',
        'Approved',
        'Cancelled',
        'Reserved',
        'Referred',
        'Resolved',
        'Reopened',
    )
    STATUS = namedtuple('STATUS', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS))

    status_details = models.TextField(null=True, blank=True)

    image_1 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to="enquiries/",
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    destination = models.PointField(blank=True, null=True)

    city = models.CharField(max_length=128, null=True, blank=True)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)


    def __str__(self):
        return "{}: {} -> {}".format(str(self.enquiry.id), str(EnquiryActivity.previous_status_choices[self.previous_status]), str(EnquiryActivity.previous_status_choices[self.status]))
