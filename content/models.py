from django.db import models
from django.utils.encoding import iri_to_uri
from django.utils.translation import gettext_lazy as _

class BasicPage(models.Model):
	url = models.CharField(_('URL'), max_length=100, db_index=True)
	title = models.CharField(_('Title'), max_length=200)
	title_zh = models.CharField(_('Title (Chinese)'), max_length=200)
	content = models.TextField(_('Content'), blank=True)
	content_zh = models.TextField(_('Content (Chinese)'), blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _('basicpage')
		verbose_name_plural = _('basicpages')
		ordering = ('url',)

	def __str__(self):
		return "%s -- %s" % (self.url, self.title)

	def get_absolute_url(self):
		return iri_to_uri(self.url)
