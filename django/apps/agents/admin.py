from django.contrib import admin

from .models import AgentSkills, Agent, AgentChanges, AgentRatings, AgentRatingsHistory

class AgentSkillsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = AgentSkills
admin.site.register(AgentSkills, AgentSkillsAdmin)

class AgentAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Agent
admin.site.register(Agent, AgentAdmin)

class AgentChangesAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = AgentChanges
admin.site.register(AgentChanges, AgentChangesAdmin)

class AgentRatingsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = AgentRatings
admin.site.register(AgentRatings, AgentRatingsAdmin)

class AgentRatingsHistoryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = AgentRatingsHistory
admin.site.register(AgentRatingsHistory, AgentRatingsHistoryAdmin)
