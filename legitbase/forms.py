from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from .models import LawyerServiceRequest

class LawyerServiceRequestForm(forms.ModelForm):
	captcha = ReCaptchaField(widget=ReCaptchaWidget())
	class Meta:
		model = LawyerServiceRequest
		fields = [
			'requester_name', 'requester_email',
			'requester_phone', 'message',
			'time_choice1', 'time_choice2', 'time_choice3',
		]
		widgets = {
		}
