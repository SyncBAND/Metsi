from django.db import models

class VehicleMake(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class VehicleBodyTypes(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class VehicleTransmission(models.Model):

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class VehicleTrims(models.Model):

    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    body_type = models.ForeignKey(VehicleBodyTypes, on_delete=models.CASCADE)
    transmission = models.ForeignKey(VehicleTransmission, on_delete=models.CASCADE)

    year = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return "{}: {} - {}, {}".format(self.make.name, self.body_type, self.transmission, self.year)

class Vehicle(models.Model):

    name = models.CharField(max_length=255, blank = True, null = True, default="")
    sub_name = models.CharField(max_length=255, blank = True, default='')

    trim = models.ForeignKey(VehicleTrims, on_delete=models.CASCADE)

    def __str__(self):
        return self.get_vehicle_name()

    def get_vehicle_name(self):
        return "{} {}, {}".format(self.name, self.sub_name, self.trim)