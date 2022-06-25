from django.contrib import admin

from .models import EnduserLevel, Enduser, EnduserChanges, EnduserRatings, EnduserRatingsHistory

class EnduserLevelAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = EnduserLevel
admin.site.register(EnduserLevel, EnduserLevelAdmin)

class EnduserAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Enduser
admin.site.register(Enduser, EnduserAdmin)

class EnduserChangesAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = EnduserChanges
admin.site.register(EnduserChanges, EnduserChangesAdmin)

class EnduserRatingsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = EnduserRatings
admin.site.register(EnduserRatings, EnduserRatingsAdmin)

class EnduserRatingsHistoryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = EnduserRatingsHistory
admin.site.register(EnduserRatingsHistory, EnduserRatingsHistoryAdmin)
