from django.db import models
from django.utils import timezone

class CreatedModifiedMixin(models.Model):

    created = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True, null = True, editable=False)
    modified = models.DateTimeField(auto_now_add = False, auto_now = True, blank = True, null = True, editable=False)
    
    class Meta:
        abstract = True
