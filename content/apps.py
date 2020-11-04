from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


class ContentConfig(AppConfig):
	name = 'content'
	verbose_name = pgettext_lazy('app name', 'content')
