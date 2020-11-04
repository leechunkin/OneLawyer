from django.db.models import Model, AutoField, ManyToManyField
from django.db.models import TextField, CharField, DateTimeField, URLField

class Category(Model):
	name_en = CharField('Name (English)', max_length=80)
	name_zh = CharField('Name (Chinese)', max_length=80)
	def __str__(self):
		return self.name_en + ' / ' + self.name_zh

class Post(Model):
	title = TextField('Title')
	author = TextField('Author')
	summary = TextField('Summary')
	content = TextField('Content')
	link = URLField('Link', null=True, blank=True)
	link_title = CharField('Link Title', max_length=80, null=True, blank=True)
	categories = ManyToManyField(Category, verbose_name='Categories')
	created = DateTimeField('created', auto_now_add=True)
	updated = DateTimeField('updated', auto_now=True)
	class Meta:
		ordering = ['-created']
