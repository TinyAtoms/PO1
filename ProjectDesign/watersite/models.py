from django.db import models
from django.urls import reverse
import datetime
from .hardware import activate_relay, getwaterlevel


class Plantgroup(models.Model):
    """This represents the plant groups, and the user edits the info here

    :param models: [description]
    :type models: [type]
    """
    location = models.IntegerField(unique=True)
    plant = models.TextField()
    kc = models.FloatField()
    area = models.FloatField()
    water_flowrate = models.FloatField()
    water_t1 = models.TimeField(default=datetime.time(12, 0, 0))
    last_irrigation = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Group {self.location} : {self.plant}"

    def get_absolute_url(self):  # when you're going to implement the detail view
        """Returns the url to access a particular  instance."""
        return reverse('plant-group-detail', args=[str(self.location)])

    class Meta:
        db_table = "Plantgroup"
        verbose_name_plural = "Plantgroups"

    def water_now(self):
        t = 5
        activate_relay(self.location, t)
        self.last_irrigation = self.water_flowrate * t


class Transipration(models.Model):
    date = models.DateField(auto_now=True)
    start_level = models.FloatField()
    last_level = models.FloatField()

    def __str__(self):
        return f"{self.date} waterlevel entry"

    def get_absolute_url(self):  # when you're going to implement the detail view
        """Returns the url to access a particular  instance. For detailfiews and such"""
        return reverse('plant-detail', args=[str(self.date)])

    class Meta:
        '''Some extra options'''
        db_table = "Transpiration"
        verbose_name_plural = "Transpiration"

    @classmethod
    def create(cls):
        '''This sets the startlevel on creation'''
        start = getwaterlevel()
        data = cls(start_level=start, last_level=start)
        return data

    def measure(self):
        '''
        Measures current waterlevel, adds water when below a treshold and keeps track of autosiphon and relay use. 
        needs to be scheduled in scheduling.py
        '''
        self.last_level = getwaterlevel()
        self.save()
        return self.last_level

    @property
    def evaporated_today(self):
        '''
        returns how much water evaporated today in mm
        '''
        return (self.last_level - self.start_level)
