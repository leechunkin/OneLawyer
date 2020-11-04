from django.db import models
import legitbase.models

class Service(models.Model):
	service = models.ForeignKey(
		legitbase.models.Category,
		related_name = '+',
		on_delete = models.CASCADE
	)
	counter = models.PositiveIntegerField('counter', default=0)

class LawyerService(models.Model):
	service = models.ForeignKey(
		legitbase.models.LawyerService,
		related_name = '+',
		on_delete = models.CASCADE
	)
	counter = models.PositiveIntegerField('counter', default=0)

class LawyerServiceRequest(models.Model):
	service = models.ForeignKey(
		legitbase.models.LawyerService,
		related_name = '+',
		on_delete=models.CASCADE
	)
	counter = models.PositiveIntegerField('counter', default=0)

class LawyerServiceSend(models.Model):
	service = models.ForeignKey(
		legitbase.models.LawyerService,
		related_name = '+',
		on_delete=models.CASCADE
	)
	counter = models.PositiveIntegerField('counter', default=0)
