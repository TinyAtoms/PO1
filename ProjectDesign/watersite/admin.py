from django.contrib import admin
from .models import Plantgroup, Transipration
# Register your models here.

admin.site.register(Plantgroup)


@admin.register(Transipration)
class TransAdmin(admin.ModelAdmin):
    '''Registers the model so it's visible in the admin page '''
    list_display = ("date", "evaporated_today")
