from django.shortcuts import render, redirect
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Plantgroup, Transipration


# Create your views here.
def group_list(request):
    all_groups = Plantgroup.objects.all().order_by('location')
    return render(request, 'watersite/group_list.html', {'groups': all_groups} )



def water_pg(request, **kwargs):
    loc = kwargs["location"]
    try:
        group = Plantgroup.objects.get(location=loc)
        group.water_now()
        evap = Transipration.objects.last().evaporated_today
        irrigation_vol = evap * group.area * group.kc / group.water_flowrate
        group.last_irrigation = irrigation_vol
        group.save()
        return HttpResponse(f"We irrigated group {loc} with %s liters." % irrigation_vol)
    except:
        group = Plantgroup.objects.filter(location=loc)

def check_waterlevel(request):
    evap = Transipration.objects.last()
    result = evap.measure()
    evap.save()
    return HttpResponse(f"water level = {result} mm")

def create_evap(request):
    today = Transipration().create()
    today.save()
    return HttpResponse(f"created entry for {today.date}")

