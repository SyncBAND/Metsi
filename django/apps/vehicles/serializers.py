from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ('id', 'name', 'title')

    def get_name(self, obj):

        return "{} {}, {}".format(obj.name, obj.sub_name, obj.trim)

    def get_title(self, obj):

        return "{} {}, {}".format(obj.name, obj.sub_name, obj.trim)
    
