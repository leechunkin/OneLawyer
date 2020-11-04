from django import forms
from django.forms import ModelForm, CharField, TextInput, Textarea
from django.contrib.admin import ModelAdmin, register
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Post

@register(Category)
class Category(ModelAdmin):
	list_display = ('name_en', 'name_zh')

@register(Post)
class PostAdmin(SummernoteModelAdmin):
	list_display = ('title', 'author', 'created', 'updated')
	filter_horizontal = ('categories',)
	summernote_fields = ('summary', 'content')
	class form(ModelForm):
		class Meta:
			widgets = {
				'title': TextInput,
				'author': TextInput
			}
