import collections
import django.core.exceptions
import django.db.models
import django.http
import django.shortcuts
import django.utils.translation
import django.contrib.auth
import django_summernote.widgets
from .. import models
from .. import utils

def error_403(request):
	return django.http.HttpResponse(
		"forbidden",
		content_type="text/plain; charset=US-ASCII",
		status=403
	)

def error_404(request):
	return django.http.HttpResponse(
		"not found",
		content_type="text/plain; charset=US-ASCII",
		status=404
	)

def error_500(request):
	return django.http.HttpResponse(
		"internal error",
		content_type="text/plain; charset=US-ASCII",
		status=500
	)

def make_trans():
	def trans_en(en, zh):
		return en or zh
	def trans_zh(en, zh):
		return zh or en
	if django.utils.translation.get_language().startswith('zh'):
		return trans_zh
	else:
		return trans_en

class LinearCategory():
	categories = None
	depth = None
	@staticmethod
	def cache():
		def fields(node, size, depth):
			data = node['data']
			return {
				'id': node['id'],
				'name': data['name'],
				'name_zh': data['name_zh'],
				'size': size,
				'depth': depth
			}
		def linearise(node, depth):
			children = node.get('children')
			if children is None:
				return [[fields(node, 1, depth)]]
			else:
				linear = [
					category
					for child in children
					for category in linearise(child, depth+1)
				]
				linear[0] = [fields(node, len(linear), depth)] + linear[0]
				return linear
		categories = [
			category
			for tree in models.Category.dump_bulk()
			for category in linearise(tree, 0)
		]
		LinearCategory.depth = max(map(len, categories))
		LinearCategory.categories = [
			{
				'id': category[-1]['id'],
				'list': category,
				'pad': LinearCategory.depth - category[-1]['depth']
			}
			for category in categories
		]
	@staticmethod
	def get_categories():
		if LinearCategory.categories is None:
			LinearCategory.cache()
		return LinearCategory.categories
	@staticmethod
	def get_depth():
		if LinearCategory.depth is None:
			LinearCategory.cache()
		return LinearCategory.depth

def is_lawfirm_admin(user, lawfirm):
	return user.is_superuser or lawfirm.admins.filter(id=user.id).exists()

def is_lawyer_admin(user, lawyer_post):
	admin = lawyer_post.admin
	return (admin and admin.id == user.id) or is_lawfirm_admin(user, lawyer_post.firm)

def login(request):
	context = {'fail' : False}
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = django.contrib.auth.authenticate(request, username=username, password=password)
		if user is not None:
			django.contrib.auth.login(request, user)
			return django.shortcuts.redirect('/lawfirm/');
		else:
			context['fail'] = True
	return django.shortcuts.render(request, 'legitbase/lawfirm/login.html', context)

def logout(request):
	django.contrib.auth.logout(request)
	return django.shortcuts.redirect('/lawfirm/');

class LawFirmFormFields:
	lawfirm = (
		'name', 'name_zh', 'address', 'address_zh',
		'email', 'phone', 'fax', 'website', 'lawsochk_profile',
	)

class LawyerFormFields:
	lawyer_post = ('post', 'post_zh', 'from_date', 'end_date', 'hourly_rate')
	lawyer = ('name', 'name_zh', 'admission_date_hk', 'email', 'phone', 'fax', 'lawsochk_profile', 'intro', 'intro_zh')
	optional = ('end_date', 'admission_date_hk')

def index(request):
	global categories_cache
	user = request.user
	if not user or not user.is_active or not user.is_authenticated:
		return login(request)
	def service_context(services):
		context = [{'category': category, 'provide': None} for category in LinearCategory.get_categories()]
		for line in context:
			if services is None:
				continue
			try:
				service = services.get(service__id=line['category']['id'])
			except django.core.exceptions.ObjectDoesNotExist:
				continue
			line['provide'] = {
				'enable': True,
				'rate': service.rate,
				'is_hourly_rate': service.is_hourly_rate,
				'time_estimate_minutes_max': service.time_estimate_minutes_max,
				'free_consultation_minutes': service.free_consultation_minutes
			}
		return context
	def lawyer_context(lawyer_post):
		lawyer = lawyer_post.lawyer
		context = {
			'id': lawyer_post.id,
			'languages': [l.glottocode for l in lawyer.languages.all()],
			'services': service_context(lawyer_post.lawyerservice_set.all()),
			'service_depth': LinearCategory.get_depth()
		}
		for field in LawyerFormFields.lawyer:
			context[field] = getattr(lawyer, field)
		for field in LawyerFormFields.lawyer_post:
			context[field] = getattr(lawyer_post, field)
		return context
	def lawfirm_context(lawfirm):
		context = {
			'id': lawfirm.id,
			'lawyers': [
				lawyer_context(lawyer_post)
				for lawyer_post in lawfirm.lawyerpost_set.all()
				if is_lawyer_admin(user, lawyer_post)
			],
			'is_lawfirm_admin': is_lawfirm_admin(user, lawfirm),
			'district': lawfirm.district.code
		}
		for field in LawFirmFormFields.lawfirm:
			context[field] = getattr(lawfirm, field)
		return context
	options = {
		'districts': models.HKDistrict.objects.all(),
		'languages': models.Language.objects.all()
	}
	lawfirms = [
		lawfirm_context(lawfirm)
		for lawfirm in list(user.lawfirm_admins.all()) + [lawyer.firm for lawyer in user.lawyer_admins.all()]
	]
	context = {
		'options': options,
		'lawfirms': lawfirms,
		'services': service_context(None),
		'service_depth': LinearCategory.get_depth(),
		'free_consultation_minutes': [
			{
				'name': choice[1],
				'value': choice[0]
			}
			for choice in models.LawyerService.FREE_CHOICES
		]
	}
	return django.shortcuts.render(request, 'legitbase/lawfirm/index.html', context)

def update(request):
	if request.method == 'POST':
		lawfirm = request.user.lawfirm_admins.get(id=request.POST['lawfirm_id'])
		if not is_lawfirm_admin(request.user, lawfirm):
			return error_403(request)
		for field in LawFirmFormFields.lawfirm:
			setattr(lawfirm, field, request.POST.get(field))
		lawfirm.district = models.HKDistrict.objects.get(code=request.POST['district'])
		lawfirm.save()
	return django.shortcuts.redirect('/lawfirm/')

ServiceEntry = collections.namedtuple(
	'ServiceEntry',
	['id', 'rate', 'is_hourly_rate', 'time_estimate_minutes_max', 'free_consultation_minutes']
)

def int_or_zero(string):
	try:
		return int(string)
	except ValueError:
		return 0

def update_services(form):
	post_id = int(form['post_id'])
	lawyer_post = models.LawyerPost.objects.get(id=post_id)
	categories = [category['id'] for category in LinearCategory.get_categories()]
	provide_ids = [n for n in categories if form.get('provide-' + str(n))]
	unprovide = [ls for ls in lawyer_post.lawyerservice_set.all() if ls.service.id not in provide_ids]
	for lawyer_service in unprovide:
		lawyer_service.delete()
	for n in provide_ids:
		s = str(n)
		lawyer_post.lawyerservice_set.update_or_create(
			service__id = n,
			defaults = {
				'service': models.Category.objects.get(id=n),
				'lawyer_post': lawyer_post,
				'rate': int_or_zero(form['rate-' + s]),
				'is_hourly_rate': form.get('hourly-' + s) is not None,
				'time_estimate_minutes_max': int_or_zero(form['estimate-' + s]),
				'free_consultation_minutes': int_or_zero(form['consultation-' + s])
			}
		)

def lawyer_update(request):
	if request.method == 'POST':
		try:
			post_id = int(request.POST['post_id'])
			lawyer_post = models.LawyerPost.objects.get(id=post_id)
		except Exception:
			post_id = None
			lawyer_post = None
		if lawyer_post is None:
			return error_404(request)
		else:
			if not is_lawyer_admin(request.user, lawyer_post):
				return error_403(request)
			lawyer = lawyer_post.lawyer
			for field in LawyerFormFields.lawyer:
				if field in LawyerFormFields.optional and request.POST.get(field) == '':
					setattr(lawyer, field, None)
				else:
					setattr(lawyer, field, request.POST.get(field))
			for field in LawyerFormFields.lawyer_post:
				if field in LawyerFormFields.optional and request.POST.get(field) == '':
					setattr(lawyer_post, field, None)
				else:
					setattr(lawyer_post, field, request.POST.get(field))
			lawyer.save()
			lawyer_post.save()
		language_codes = utils.dict_prefix(request.POST, 'language-').keys()
		language_objects = (models.Language.objects.get(glottocode=code) for code in language_codes)
		lawyer.languages.set(language_objects)
	if request.method == 'POST':
		update_services(request.POST)

	return django.shortcuts.redirect('/lawfirm/')
