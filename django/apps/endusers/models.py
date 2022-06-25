from django.conf import settings
from django.db import models

from apps.user_profile.models import UserProfile
from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator

from collections import namedtuple

# https://stackoverflow.com/questions/20895429/how-exactly-do-django-content-types-work
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class EnduserLevel(CreatedModifiedMixin):

    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Enduser(CreatedModifiedMixin):
    
    enduser = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    level_choices = (
        'FIRST_YEAR',
        'SECOND_YEAR',
        'THIRD_YEAR',
        'Honours',
        'Masters',
        'PhD',
    )
    LEVEL_TYPE = namedtuple('LEVEL_TYPE', level_choices)(*range(0, len(level_choices)))
    level = models.PositiveIntegerField(default=0, choices=get_field_choices(LEVEL_TYPE))

    pending = models.PositiveIntegerField(default=0)
    cancelled = models.PositiveIntegerField(default=0)
    approved = models.PositiveIntegerField(default=0)
    resolved = models.PositiveIntegerField(default=0)

    adverts = models.PositiveIntegerField(default=0)

    total_payment = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    enduser_key = models.CharField(max_length=64, unique=True)

    verified_nasfas = models.BooleanField(default=False)

    # -- ratings given to agent by enduser --#
    # to get rating percentage = (total_sum_of_ratings_for_agents/5)/total_number_of_ratings_for_agents
    total_sum_of_ratings_for_agents = models.PositiveIntegerField(default=0)
    total_number_of_ratings_for_agents = models.PositiveIntegerField(default=0)
    # -- end ratings for --#

    # -- ratings from agent given to enduser --#
    # to get rating percentage = (total_sum_of_ratings_from_agents/5)/total_number_of_ratings_from_agents
    total_sum_of_ratings_from_agents = models.PositiveIntegerField(default=0)
    total_number_of_ratings_from_agents = models.PositiveIntegerField(default=0)
    # -- end ratings from --#

    def save(self, *args, **kwargs):
        if not self.enduser_key:
            while True:
                enduser_key = random_generator(length=9, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(enduser_key=enduser_key).only('enduser_key').exists():
                    break
            self.enduser_key = enduser_key
        return super(Enduser, self).save(*args, **kwargs)

    def __str__(self):
        return self.enduser.user.first_name

class EnduserChanges(CreatedModifiedMixin):
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    # For agent

    level_choices = (
        'First_YEAR',
        'SECOND_YEAR',
        'THIRD_YEAR',
        'Honours',
        'Masters',
        'PhD',
    )
    LEVEL_TYPE = namedtuple('LEVEL_TYPE', level_choices)(*range(0, len(level_choices)))
    previous_level = models.PositiveIntegerField(default=0, choices=get_field_choices(LEVEL_TYPE))

    previous_document_cv = models.FileField(blank=True, null=True, upload_to=str("endusers/")+"/nasfas/")
    previous_document_extra = models.FileField(blank=True, null=True, upload_to="endusers/")

    # --- end for agent ---

    def __str__(self):
        return self.user.first_name


class EnduserRatings(CreatedModifiedMixin):

    user_profile_making_rating = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    enduser_being_rated = models.ForeignKey(Enduser, on_delete=models.CASCADE)

    mode_choices = (
        'ENDUSER',
        'AGENT',
    )
    MODE_TYPE = namedtuple('MODE_TYPE', mode_choices)(*range(0, len(mode_choices)))
    mode = models.PositiveIntegerField(default=0, choices=get_field_choices(MODE_TYPE))

    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(null=True, blank=True)

    editted = models.BooleanField(default=False)

    # because of ratings that could be from different apps - e.g support or enquiries
    # currently just enquiries
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return "{} rated {}".format(str(self.user_profile_making_rating.user.first_name), str(self.enduser_being_rated.enduser.user.first_name))


class EnduserRatingsHistory(CreatedModifiedMixin):

    enduser_ratings = models.ForeignKey(EnduserRatings, on_delete=models.CASCADE)

    previous_rating = models.PositiveIntegerField(default=0)
    previous_review = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} updated rating {}".format(str(self.enduser_ratings.user_profile_making_rating.user.first_name), str(self.enduser_ratings.enduser_being_rated.enduser.user.first_name))