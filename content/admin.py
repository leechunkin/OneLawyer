from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BasicPage

@admin.register(BasicPage)
class BasicPageAdmin(SummernoteModelAdmin):
	list_display = ('url', 'title', 'title_zh')
	search_fields = ('url', 'title', 'title_zh')
	summernote_fields = ('content', 'content_zh')
	fields = ('url', 'title', 'content', 'title_zh', 'content_zh')
