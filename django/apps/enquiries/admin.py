from django.contrib import admin

from .models import Enquiry, EnquiryActivity

class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Enquiry
admin.site.register(Enquiry, EnquiryAdmin)

class EnquiryActivityAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = EnquiryActivity
admin.site.register(EnquiryActivity, EnquiryActivityAdmin)

