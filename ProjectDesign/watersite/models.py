from django.db import models
from django.urls import reverse
import datetime
from .hardware import activate_relay, getwaterlevel
from numpy import array, average


class Plantgroup(models.Model):
    """This represents the plant groups, and the user edits the info here

    :param models: [description]
    :type models: [type]
    """
    location = models.IntegerField(unique=True, help_text="The number  of the solenoid valve this plant group is connected to. Has to be unique.")
    plant = models.TextField(help_text="Name of the plant.")
    kc = models.FloatField(
        help_text="dimmensionless plant coefficient. See <a href='http://www.fao.org/3/x0490e/x0490e0b.htm#crop%20coefficients'>this page</a> to find the coefficient of your crop. If you aren't sure, use the value of 1.")
    area = models.FloatField(help_text="area of the plant group in square meters.")
    water_flowrate = models.FloatField(help_text="flowrate through the valve in liters/min.")
    water_t1 = models.TimeField(default=datetime.time(12, 0, 0), help_text="Time at which the plant should be watered every day.")
    last_irrigation = models.FloatField(null=True, blank=True, help_text="How much liter water was used in the last irrigation. Leave this empty.")

    def __str__(self):
        return f"Group {self.location} : {self.plant}"

    def get_absolute_url(self):  # when you're going to implement the detail view
        """Returns the url to access a particular  instance."""
        return reverse('plant-group-detail', args=[str(self.location)])

    class Meta:
        db_table = "Plantgroup"
        verbose_name_plural = "Plantgroups"

    def water_now(self):
        """This is the function that calculates how long the relay should be activated for.
        This then sends a signal to the relay.
        """
        evap = [i.evaporated_today for i in Transipration.objects.all()
                ]
        evap.reverse()
        evap = evap[0:2]
        evap = sum(evap)  # ET0 from today and yesterday, mm

        pk = get_pan_coeff()  # pan coeff, dimmensionless
        et0 = evap * pk * self.kc
        volume = et0 * self.area  # mm * m^2 = dm^3
        volume -= self.last_irrigation
        activation_time = volume / (self.water_flowrate / 60)
        if activation_time < 0:
            return volume
        activate_relay(self.location, activation_time)
        self.last_irrigation = volume
        self.save()
        return volume


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
        diff = self.last_level - self.start_level
        if diff > 50:
            diff -= 100
        elif diff < -50:
            diff += 50
        return (diff)



# finding the correct Kp
def get_pan_coeff():
    FAO_data = [3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.1, 3.1, 3.1, 3.11, 3.11, 3.12, 3.12, 3.13, 3.14, 3.15, 3.15, 3.16, 3.17, 3.18, 3.19, 3.2, 3.21, 3.22, 3.23, 3.24, 3.25, 3.27, 3.28, 3.29, 3.3, 3.32, 3.33, 3.34, 3.35, 3.37, 3.38, 3.4, 3.41, 3.42, 3.44, 3.45, 3.46, 3.48, 3.49, 3.51, 3.52, 3.53, 3.55, 3.56, 3.57, 3.59, 3.6, 3.61, 3.63, 3.64, 3.65, 3.66, 3.67, 3.69, 3.7, 3.71, 3.72, 3.73, 3.74, 3.75, 3.76, 3.77, 3.77, 3.78, 3.79, 3.8, 3.8, 3.81, 3.81, 3.82, 3.82, 3.83, 3.83, 3.83, 3.84, 3.84, 3.84, 3.84, 3.84, 3.84, 3.84, 3.84, 3.84, 3.83, 3.83, 3.83, 3.82, 3.82, 3.81, 3.81, 3.8, 3.79, 3.79, 3.78, 3.77, 3.76, 3.75, 3.75, 3.74, 3.73, 3.72, 3.71, 3.7, 3.69, 3.67, 3.66, 3.65, 3.64, 3.63, 3.62, 3.61, 3.6, 3.58, 3.57, 3.56, 3.55, 3.54, 3.53, 3.52, 3.51, 3.5, 3.49, 3.48, 3.47, 3.46, 3.45, 3.44, 3.43, 3.42, 3.42, 3.41, 3.4, 3.39, 3.39, 3.38, 3.38, 3.37, 3.37, 3.37, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.36, 3.37, 3.37, 3.38, 3.38, 3.39, 3.39, 3.4, 3.4, 3.41, 3.42, 3.43, 3.43, 3.44, 3.45, 3.46, 3.47, 3.48, 3.49, 3.5, 3.51, 3.53, 3.54, 3.55, 3.56, 3.57, 3.59,
                3.6, 3.61, 3.63, 3.64, 3.65, 3.67, 3.68, 3.7, 3.71, 3.73, 3.74, 3.76, 3.77, 3.79, 3.8, 3.82, 3.83, 3.85, 3.87, 3.88, 3.9, 3.91, 3.93, 3.95, 3.96, 3.98, 4, 4.01, 4.03, 4.05, 4.06, 4.08, 4.1, 4.12, 4.13, 4.15, 4.17, 4.18, 4.2, 4.22, 4.23, 4.25, 4.27, 4.28, 4.3, 4.31, 4.33, 4.35, 4.36, 4.38, 4.39, 4.41, 4.42, 4.44, 4.45, 4.47, 4.48, 4.49, 4.5, 4.52, 4.53, 4.54, 4.55, 4.56, 4.57, 4.58, 4.59, 4.6, 4.61, 4.62, 4.63, 4.63, 4.64, 4.64, 4.65, 4.65, 4.66, 4.66, 4.66, 4.66, 4.67, 4.67, 4.67, 4.67, 4.66, 4.66, 4.66, 4.66, 4.65, 4.65, 4.64, 4.63, 4.63, 4.62, 4.61, 4.6, 4.59, 4.58, 4.57, 4.56, 4.55, 4.53, 4.52, 4.51, 4.49, 4.48, 4.46, 4.44, 4.43, 4.41, 4.39, 4.37, 4.35, 4.33, 4.31, 4.29, 4.27, 4.25, 4.23, 4.21, 4.19, 4.16, 4.14, 4.12, 4.09, 4.07, 4.04, 4.02, 4, 3.97, 3.95, 3.92, 3.9, 3.87, 3.85, 3.82, 3.8, 3.77, 3.75, 3.72, 3.7, 3.67, 3.65, 3.62, 3.6, 3.58, 3.55, 3.53, 3.51, 3.49, 3.46, 3.44, 3.42, 3.4, 3.38, 3.36, 3.34, 3.33, 3.31, 3.29, 3.28, 3.26, 3.24, 3.23, 3.22, 3.2, 3.19, 3.18, 3.17, 3.16, 3.15, 3.14, 3.13, 3.12, 3.12, 3.11, 3.11, 3.1, 3.1, 3.09, 3.09, 3.09, 3.77, 3.09, 4.67]
    pan_data = [(i.date.timetuple().tm_yday, i.evaporated_today)
                for i in Transipration.objects.all()]
    try:
        pan_data = pan_data[0:-1]
    except IndexError:# The only time this won't work, is the first day, in which case i want 1
        return 1
    if len(pan_data) < 10:
        return 1
    
    FAO_data = array([FAO_data[i[0]] for i in pan_data])
    pan_data = array([i[1] for i in pan_data])
    Kp = average(pan_data/FAO_data)
    return Kp
