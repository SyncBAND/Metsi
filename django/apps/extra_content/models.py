from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.user_profile.models import UserProfile
from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices

from collections import namedtuple
from versatileimagefield.fields import VersatileImageField, PPOIField

 
class ExtraContent(CreatedModifiedMixin):

    title = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    extra_content_status_choices = (
        'Active',
        'Deactivated',
        'Deleted',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', extra_content_status_choices)(*range(0, len(extra_content_status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))

    extra_content_choices = (
        'Tutorial',
        'Advert',
    )
    TYPE = namedtuple('TYPE', extra_content_choices)(*range(0, len(extra_content_choices)))
    extra_content_type = models.PositiveIntegerField(default=0, choices=get_field_choices(TYPE))

    url = models.URLField(null=True, blank=True)
    url_interactions = models.PositiveIntegerField(default=0)
    seen = models.PositiveIntegerField(default=0)

    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(default=timezone.now)

    # to get rating percentage = (total_sum_of_ratings/5)/total_number_of_ratings
    total_sum_of_ratings = models.PositiveIntegerField(default=0)
    total_number_of_ratings = models.PositiveIntegerField(default=0)

    image_1 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to='tutorials/',
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    city = models.CharField(max_length=128, null=True, blank=True)
    suburb = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    location = models.CharField(max_length=128, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)

    latitude = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.title


class ExtraContentActivity(CreatedModifiedMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="extra_content_activity")
    
    extra_content = models.ForeignKey(ExtraContent, on_delete=models.CASCADE)

    # TODO: handle re-activations, payments for ads
    def __str__(self):
        return "{}. {} - {}".format(self.id, self.extra_content.title, self.user.first_name)


class ExtraContentRatings(CreatedModifiedMixin):

    user_profile_making_rating = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    extra_content_being_rated = models.ForeignKey(ExtraContent, on_delete=models.CASCADE)

    mode_choices = (
        'ENDUSER',
        'AGENT',
    )
    MODE_TYPE = namedtuple('MODE_TYPE', mode_choices)(*range(0, len(mode_choices)))
    mode = models.PositiveIntegerField(default=0, choices=get_field_choices(MODE_TYPE))

    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(null=True, blank=True)

    editted = models.BooleanField(default=False)

    def __str__(self):
        return "{} rated {}: ".format(str(self.user_profile_making_rating.user.first_name), str(self.extra_content_being_rated.title))


class ExtraContentRatingsHistory(CreatedModifiedMixin):

    extra_content_ratings = models.ForeignKey(ExtraContentRatings, on_delete=models.CASCADE)

    previous_rating = models.PositiveIntegerField(default=0)
    previous_review = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} changed rating on {}: ".format(str(self.extra_content_ratings.user_profile_making_rating.user.first_name), str(self.extra_content_ratings.extra_content_being_rated.title))