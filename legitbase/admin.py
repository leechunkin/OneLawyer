from datetime import date
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from ordered_model.admin import OrderedModelAdmin, OrderedTabularInline
from django_summernote.settings import get_attachment_model
from .models import Category, LawFirm, Lawyer, LawyerPost, LawyerService
from .models import Panel, LawyerPanel
from .models import Jurisdiction, LawyerJurisdiction
from .models import HKDistrict, Language, Experience, ItemRate
from .models import OptionalIntro, OptionalResume, OptionalResumeEntry
from .models import OptionalContact, OptionalMedia, OptionalCase
from .models import LawyerServiceRequest

admin.site.site_header = _('LEGIT administration')
admin.site.site_title = _('LEGIT site admin')

def is_lawfirm_admin(user, obj=None):
	return (not user.is_superuser) and user.has_perm('legitbase.admin_firm', obj)

def is_lawyer_admin(user, obj=None):
	return (not user.is_superuser) and user.has_perm('legitbase.admin_lawyer', obj)

class ServiceChoiceField(forms.ModelChoiceField):
	def name_key(self):
		lang = translation.get_language()
		if lang.startswith('zh'):
			return 'name_zh'
		else:
			return 'name'

	def label_from_instance(self, obj):
		path = list(obj.get_ancestors())
		path.append(obj)
		name_key = self.name_key()
		return " > ".join([getattr(c, name_key) for c in path])

class AlwaysChangedModelForm(forms.ModelForm):
	def has_changed(self):
		""" Should returns True if data differs from initial.
		By always returning true even unchanged inlines will get validated and saved."""
		return True

@admin.register(Category)
class CategoryAdmin(TreeAdmin):
	form = movenodeform_factory(Category)
	list_display = ('category_name',)
	list_per_page = 200

	def category_name(self, obj):
		return '%d. %s %s' % (obj.order, obj.name_zh, obj.name)
	category_name.short_description = _('Name')

class LawyerServiceInline(admin.TabularInline):
	model = LawyerService
	extra = 1

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'service':
			return ServiceChoiceField(queryset=Category.objects.filter(numchild=0))
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

class LawyerPanelInline(OrderedTabularInline):
	model = LawyerPanel
	fields = ['panel', 'order', 'move_up_down_links']
	readonly_fields = ['order', 'move_up_down_links']
	extra = 1
	ordering = ['order']

class LawyerPostInline(admin.TabularInline):
	model = LawyerPost
	extra = 1
	autocomplete_fields = ['lawyer', 'firm']

class LawyerJurisdictionInline(admin.TabularInline):
	model = LawyerJurisdiction
	extra = 1


class SubscriptionEndDateListFilter(admin.SimpleListFilter):
	title = _('Subscription End Date')
	parameter_name = 'sub_ended'

	def lookups(self, request, model_admin):
		return (
			('0', _('Not Ended')),
			('1', _('Ended')),
		)

	def queryset(self, request, qs):
		today = date.today()
		if self.value() == '0':
			return qs.filter(subscription_end_date__lt=today)
		if self.value() == '1':
			return qs.filter(subscription_end_date__gte=today)

@admin.register(LawFirm)
class LawFirmAdmin(admin.ModelAdmin):
	inlines = (LawyerPostInline,)
	filter_horizontal = ['admins']
	search_fields = ['name', 'name_zh']
	list_display = ['name', 'name_zh', 'status', 'subscription_end_date']
	list_filter = ['status', SubscriptionEndDateListFilter, 'district']
	date_hierarchy = 'subscription_end_date'

	def get_exclude(self, request, obj=None):
		excluded = list(super().get_exclude(request, obj) or [])
		excluded.append('subscription_nag_sent')
		if is_lawfirm_admin(request.user):
			return excluded + ['remarks', 'status', 'admins', 'subscription_start_date', 'subscription_end_date']
		return excluded

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		user = request.user
		if is_lawfirm_admin(user):
			qs = qs.filter(admins__id__contains=user.id)
		return qs

	def has_change_permission(self, request, obj=None):
		user = request.user
		if obj is not None and is_lawfirm_admin(user):
			return obj.admins.filter(id=user.id).exists()
		return super().has_change_permission(request, obj)


@admin.register(OptionalIntro)
class OptionalIntro(admin.ModelAdmin):
	pass

class OptionalResumeEntryInline(admin.TabularInline):
	model = OptionalResumeEntry
	extra = 1

@admin.register(OptionalResume)
class OptionalResumeAdmin(admin.ModelAdmin):
	inlines = [OptionalResumeEntryInline]

@admin.register(OptionalContact)
class OptionalContactAdmin(admin.ModelAdmin):
	pass

@admin.register(OptionalMedia)
class OptionalMediaAdmin(admin.ModelAdmin):
	pass

@admin.register(OptionalCase)
class OptionalCaseAdmin(OrderedModelAdmin):
	list_display = ['lawyer', 'code', 'order', 'move_up_down_links']
	list_display_links = ['lawyer', 'code']

@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
	inlines = [LawyerJurisdictionInline, LawyerPostInline]
	search_fields = ['name', 'name_zh']
	list_display = ['name', 'name_zh']
	filter_horizontal = ['languages']

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if is_lawfirm_admin(request.user):
			qs = qs.filter(firms__admins__id__contains=request.user.id)
		return qs

	def has_change_permission(self, request, obj=None):
		user = request.user
		if obj is not None and is_lawfirm_admin(user):
			return obj.firms.filter(admins__id__contains=user.id).exists()
		if obj is not None and is_lawyer_admin(user):
			return obj.lawyerpost_set.filter(admin__id=user.id).exists()
		return super().has_change_permission(request, obj)


@admin.register(LawyerPost)
class LawyerPostAdmin(admin.ModelAdmin):
	inlines = [LawyerPanelInline, LawyerServiceInline]
	list_display = ['lawyer', 'firm', 'post', 'post_zh']
	list_display_links = ['firm', 'lawyer']
	search_fields = ['firm__name', 'firm__name_zh', 'lawyer__name', 'lawyer__name_zh']
	autocomplete_fields = ['lawyer', 'firm']

	def get_exclude(self, request, obj=None):
		excluded = list(super().get_exclude(request, obj) or [])
		if is_lawfirm_admin(request.user):
			return excluded + ['precedence', 'lawyer_admins']
		return excluded

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if is_lawfirm_admin(request.user):
			qs = qs.filter(firm__admins__id__contains=request.user.id)
		return qs

	def has_change_permission(self, request, obj=None):
		user = request.user
		if obj is not None and is_lawyer_admin(user):
			return obj.admin.id == user.id
		return super().has_change_permission(request, obj)

	def get_urls(self):
		urls = super().get_urls()
		for inline in self.inlines:
			if hasattr(inline, 'get_urls'):
				urls = inline.get_urls(self) + urls
		return urls

	def get_inline_instances(self, request, obj=None):
		return [
			inline(self.model, self.admin_site)
			for inline in self.inlines
			if request.user.is_superuser or inline is LawyerServiceInline
		]


@admin.register(Jurisdiction)
class JurisdictionAdmin(admin.ModelAdmin):
	pass

@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
	list_display = ('name',)

@admin.register(HKDistrict)
class HKDistrictAdmin(admin.ModelAdmin):
	list_display = ('region', 'name', 'name_zh', 'code')
	list_display_links = ('region', 'code')
	list_filter = ('region',)
	list_editable = ('name', 'name_zh')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
	list_display = ('glottocode', 'name', 'name_zh', 'iso639_3')
	list_display_links = ('glottocode',)
	list_editable = ('name', 'name_zh', 'iso639_3')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
	list_display = ('yearFrom', 'yearTo', 'desc', 'desc_zh')
	list_display_links = ('yearFrom', 'yearTo')
	list_editable = ('desc', 'desc_zh')

@admin.register(ItemRate)
class ExperienceAdmin(admin.ModelAdmin):
	list_display = ('rateFrom', 'rateTo', 'desc', 'desc_zh')
	list_display_links = ('rateFrom', 'rateTo')
	list_editable = ('desc', 'desc_zh')


class LawFirmAdminInline(admin.StackedInline):
	model = LawFirm.admins.through
	extra = 1
	autocomplete_fields = ['lawfirm']
	verbose_name = 'Law Firm'
	verbose_name_plural = 'Admin of Law Firms'

class UserAdmin(BaseUserAdmin):
	inlines = (LawFirmAdminInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# remove Attachment from admin
admin.site.unregister(get_attachment_model())

if settings.DEBUG:
	@admin.register(LawyerServiceRequest)
	class LawyerServiceRequestAdmin(admin.ModelAdmin):
		list_display = ['requester_name', 'requester_email']
