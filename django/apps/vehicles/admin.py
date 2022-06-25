from django.contrib import admin

from .models import VehicleMake, VehicleBodyTypes, VehicleTransmission, VehicleTrims, Vehicle

class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = VehicleMake

admin.site.register(VehicleMake, VehicleMakeAdmin)

class VehicleBodyTypesAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = VehicleBodyTypes

admin.site.register(VehicleBodyTypes, VehicleBodyTypesAdmin)

class VehicleTransmissionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = VehicleTransmission

admin.site.register(VehicleTransmission, VehicleTransmissionAdmin)

class VehicleTrimsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = VehicleTrims

admin.site.register(VehicleTrims, VehicleTrimsAdmin)

class VehicleAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Vehicle

admin.site.register(Vehicle, VehicleAdmin)