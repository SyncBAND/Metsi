from django.conf import settings
from django.db import models

# https://stackoverflow.com/questions/20895429/how-exactly-do-django-content-types-work
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
#from django.contrib.postgres.fields import ArrayField

from apps.user_profile.models import UserProfile
from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator

from collections import namedtuple
from versatileimagefield.fields import VersatileImageField, PPOIField

 
class AgentSkills(CreatedModifiedMixin):

    title = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Agent(CreatedModifiedMixin):
    
    agent = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    #skills = ArrayField(models.TextField(blank=True), null=True)
    skills = models.ManyToManyField(AgentSkills, blank=True)

    document_cv = models.FileField(blank=True, null=True, upload_to="agents/documents")
    document_extra = models.FileField(blank=True, null=True, upload_to="agents/documents")
    document_extra_1 = models.FileField(blank=True, null=True, upload_to="agents/documents")

    payment_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    call_out_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    agent_key = models.CharField(max_length=64, unique=True)

    reserved = models.PositiveIntegerField(default=0)
    referred = models.PositiveIntegerField(default=0)
    cancelled = models.PositiveIntegerField(default=0)
    resolved = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=False)

    agent_choices = (
        'Active',
        'Deactivated',
        'Deleted',
    )
    TYPE = namedtuple('TYPE', agent_choices)(*range(0, len(agent_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(TYPE))

    # -- ratings given to enduser by agent --#
    # to get rating percentage = (total_sum_of_ratings_for_endusers/5)/total_number_of_ratings_for_endusers
    total_sum_of_ratings_for_endusers = models.PositiveIntegerField(default=0)
    total_number_of_ratings_for_endusers = models.PositiveIntegerField(default=0)
    # -- end ratings for --#

    # -- ratings from endusers given to agent --#
    # to get rating percentage = (total_sum_of_ratings_from_endusers/5)/total_number_of_ratings_from_endusers
    total_sum_of_ratings_from_endusers = models.PositiveIntegerField(default=0)
    total_number_of_ratings_from_endusers = models.PositiveIntegerField(default=0)
    # -- end ratings from --#


    image_1 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    image_3 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_3',
        null=True, blank=True
    )
    image_ppoi_3 = PPOIField()

    image_4 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_4',
        null=True, blank=True
    )
    image_ppoi_4 = PPOIField()

    image_5 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_5',
        null=True, blank=True
    )
    image_ppoi_5 = PPOIField()

    image_6 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_6',
        null=True, blank=True
    )
    image_ppoi_6 = PPOIField()

    image_7 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_7',
        null=True, blank=True
    )
    image_ppoi_7 = PPOIField()

    image_8 = VersatileImageField(
        'Image',
        upload_to='agents/',
        ppoi_field='image_ppoi_8',
        null=True, blank=True
    )
    image_ppoi_8 = PPOIField()

    def save(self, *args, **kwargs):
        if not self.agent_key:
            while True:
                agent_key = random_generator(length=9, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(agent_key=agent_key).only('agent_key').exists():
                    break
            self.agent_key = agent_key
        return super(Agent, self).save(*args, **kwargs)

    def __str__(self):
        return self.agent.user.first_name

class AgentChanges(CreatedModifiedMixin):
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    # For agent

    previous_skills = models.ManyToManyField(AgentSkills, blank=True)

    previous_document_cv = models.FileField(blank=True, null=True, upload_to="agents/documents")
    previous_document_extra = models.FileField(blank=True, null=True, upload_to="agents/documents")
    previous_document_extra_1 = models.FileField(blank=True, null=True, upload_to="agents/documents")

    status = models.PositiveIntegerField(null=True, blank=True)

    # --- end for agent ---

    def __str__(self):
        return self.agent.user.first_name

class AgentRatings(CreatedModifiedMixin):

    user_profile_making_rating = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent_being_rated = models.ForeignKey(Agent, on_delete=models.CASCADE)

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
        return "{} rated {}".format(str(self.user_profile_making_rating.user.first_name), str(self.agent_being_rated.agent.user.first_name))


class AgentRatingsHistory(CreatedModifiedMixin):

    agent_ratings = models.ForeignKey(AgentRatings, on_delete=models.CASCADE)

    previous_rating = models.PositiveIntegerField(default=0)
    previous_review = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} updated rating on {}".format(str(self.agent_ratings.user_profile_making_rating.user.first_name), str(self.agent_ratings.agent_being_rated.agent.user.first_name))