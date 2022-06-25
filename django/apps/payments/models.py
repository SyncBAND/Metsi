from django.conf import settings
from django.db import models

from apps.user_profile.models import UserProfile
from apps.utils.models import CreatedModifiedMixin
from apps.utils.views import get_field_choices, random_generator
from apps.agents.models import Agent

from versatileimagefield.fields import VersatileImageField, PPOIField

from collections import namedtuple

# https://stackoverflow.com/questions/20895429/how-exactly-do-django-content-types-work
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

    
class Invoice(CreatedModifiedMixin):

    invoiced_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="invoiced_by")
    invoiced_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="invoiced_to")

    reference = models.CharField(max_length=32, null=False)

    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    mode_choices = (
        'ENDUSER',
        'AGENT',
    )
    MODE_TYPE = namedtuple('MODE_TYPE', mode_choices)(*range(0, len(mode_choices)))
    mode = models.PositiveIntegerField(default=0, choices=get_field_choices(MODE_TYPE))

    status_choices = (
        'Active',
        'Cancelled',
        'Paid',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                reference = random_generator(length=9, letters=True, digits=True, punctuation=False)
                if not type(self).objects.filter(reference=reference).only('reference').exists():
                    break
            self.reference = reference
        return super(Invoice, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.reference)

class InvoiceCancelled(CreatedModifiedMixin):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    cancelled_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.invoice.reference)

class Payment(CreatedModifiedMixin):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    reference = models.CharField(max_length=32, null=False)

    total_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    image_1 = VersatileImageField(
        'Image',
        upload_to="payments/",
        ppoi_field='image_ppoi_1',
        null=True, blank=True
    )
    image_ppoi_1 = PPOIField()

    image_2 = VersatileImageField(
        'Image',
        upload_to="payments/",
        ppoi_field='image_ppoi_2',
        null=True, blank=True
    )
    image_ppoi_2 = PPOIField()

    proof_of_payment = models.FileField(blank=True, null=True, upload_to="payments/")
    extra_documents = models.FileField(blank=True, null=True, upload_to="payments/")

    status_choices = (
        'Paid',
        'Refunded',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(blank=True, null=True)
        
    def __str__(self):
        return str(self.invoice.reference)

class PaymentRefunded(CreatedModifiedMixin):

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    refunded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    status_choices = (
        'Pending',
        'Successful',
    )
    STATUS_TYPE = namedtuple('STATUS_TYPE', status_choices)(*range(0, len(status_choices)))
    status = models.PositiveIntegerField(default=0, choices=get_field_choices(STATUS_TYPE))
    status_details = models.TextField(blank=True, null=True)

    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.invoice.reference)