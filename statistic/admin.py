from django.contrib import admin
from .models import Service
from .models import LawyerService, LawyerServiceRequest, LawyerServiceSend

@admin.register(Service)
class LawyerServiceAdmin(admin.ModelAdmin):
	list_display = ['service', 'counter']
	list_editable = ['counter']
	ordering = ['-counter']

@admin.register(LawyerService)
class LawyerServiceAdmin(admin.ModelAdmin):
	list_display = ['service', 'counter']
	list_editable = ['counter']
	ordering = ['-counter']

@admin.register(LawyerServiceRequest)
class LawyerServiceRequestAdmin(admin.ModelAdmin):
	list_display = ['service', 'counter']
	list_editable = ['counter']
	ordering = ['-counter']

@admin.register(LawyerServiceSend)
class LawyerServiceRequestAdmin(admin.ModelAdmin):
	list_display = ['service', 'counter']
	list_editable = ['counter']
	ordering = ['-counter']
