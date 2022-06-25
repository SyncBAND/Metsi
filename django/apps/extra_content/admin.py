from django.contrib import admin

from .models import ExtraContent, ExtraContentActivity

class ExtraContentAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = ExtraContent
        
admin.site.register(ExtraContent, ExtraContentAdmin)

class ExtraContentActivityAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = ExtraContentActivity
        
admin.site.register(ExtraContentActivity, ExtraContentActivityAdmin)

