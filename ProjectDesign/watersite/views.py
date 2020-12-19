from django.shortcuts import render, redirect
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Plantgroup, Transipration


# Create your views here.


def group_list(request):
    all_groups = Plantgroup.objects.all().order_by('location')
    return render(request, 'watersite/group_list.html', {'groups': all_groups})


def water_pg(request, **kwargs):
    loc = kwargs["location"]
    group = Plantgroup.objects.get(location=loc)
    vol = group.water_now()
    return HttpResponse(f"We irrigated group {loc} with {vol} liters.")



def check_waterlevel(request):
    evap = Transipration.objects.last()
    result = evap.measure()
    evap.save()
    return HttpResponse(f"water level = {result} mm")


def create_evap(request):
    today = Transipration().create()
    today.save()
    return HttpResponse(f"created entry for {today.date}")



