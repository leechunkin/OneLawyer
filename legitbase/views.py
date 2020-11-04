import math
import random
import json
import uuid
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import translation
from django.utils.cache import patch_cache_control

from .models import Category, HKDistrict, Language, Experience, ItemRate
from .models import LawyerPost, LawyerService, LawyerServiceRequest
from .models import LawyerEndorsement, RequestEndorsement
from .forms import LawyerServiceRequestForm
from .utils import limit_number, resolve_name_by_lang
import statistic

def full_service_path(service, resolve_name):
	full_path = list(service.get_ancestors())
	full_path.append(service)
	return [
		resolve_name(part.name, part.name_zh)
		for part in full_path
	]

def full_service_path_id(service):
	full_path = list(service.get_ancestors())
	full_path.append(service)
	return [part.id for part in full_path]

def set_session_language(request):
	lang = translation.get_language()
	if lang.startswith('zh'):
		lang = 'zh'
	else:
		lang = 'en'
	translation.activate(lang)
	if hasattr(request, 'session'):
		request.session[translation.LANGUAGE_SESSION_KEY] = lang
	return lang

def browse_filters(l10n):
	return {
		'districts': [
			{
				'region': district.region,
				'code': district.code,
				'name': l10n(district.name, district.name_zh)
			}
			for district in HKDistrict.objects.all()
		],
		'languages': [
			{
				'glottocode': language.glottocode,
				'iso639_3': language.iso639_3,
				'name': l10n(language.name, language.name_zh)
			}
			for language in Language.objects.all()
		],
		'experience': [
			{
				'from': e.yearFrom,
				'to': e.yearTo,
				'desc': l10n(e.desc, e.desc_zh)
			}
			for e in Experience.objects.order_by('yearFrom').all()
		],
		'rates': [
			{
				'from': rate.rateFrom,
				'to': rate.rateTo,
				'desc': l10n(rate.desc, rate.desc_zh)
			}
			for rate in ItemRate.objects.order_by('rateFrom').all()
		]
	}

def index(request):
	context = browse_filters(resolve_name_by_lang(set_session_language(request)))
	context.update({'regions': HKDistrict.REGIONS})
	return render(request, 'index.html', context)


categories_cached = None

def cache_categories():
	global categories_cached
	def purify(node):
		data = node.get('data')
		if data is not None:
			keys = list(data.keys())
			for key in keys:
				if key not in ['name', 'name_zh']:
					del data[key]
		children = node.get('children')
		if children is not None:
			for child in children:
				purify(child)
	categories = Category.dump_bulk()
	for node in categories:
		purify(node)
	categories_cached = 'var categories=' + json.dumps(categories) + ';'

def categories(request):
	if categories_cached is None:
		cache_categories()
	response = HttpResponse(
		categories_cached,
		content_type='application/ecmascript'
	)
	patch_cache_control(response, max_age=604800)
	return response


filters_forward_table = (
	'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	'abcdefghijklmnopqrstuvwxyz'
	'0123456789-_'
)
filters_backward_table = {}
for i in range(0, len(filters_forward_table)):
	filters_backward_table[filters_forward_table[i]] = i

def decode_filters(filters, code):
	names = []
	for district in filters['districts']:
		names.append('D'+district['code'])
	for language in filters['languages']:
		names.append('L'+language['glottocode'])
	for experience in filters['experience']:
		names.append('E'+str(experience['from'])+'.'+str(experience['to']))
	for rate in filters['rates']:
		names.append('R'+str(rate['from'])+'.'+str(rate['to']))
	names.sort()
	checked = []
	for i in range(0, len(names)):
		c = i//6
		b = i - c*6
		if code is not None and c < len(code):
			n = filters_backward_table.get(code[c])
			if n is None:
				n = 0b111111
		else:
			n = 0b111111
		if n & (1 << b) != 0:
			checked.append(names[i])
	return checked

def set_checked_filters(filters, checked):
	for district in filters['districts']:
		district['checked'] = 'D'+district['code'] in checked
	for language in filters['languages']:
		language['checked'] = 'L'+language['glottocode'] in checked
	for experience in filters['experience']:
		experience['checked'] = 'E'+str(experience['from'])+'.'+str(experience['to']) in checked
	for rate in filters['rates']:
		rate['checked'] = 'R'+str(rate['from'])+'.'+str(rate['to']) in checked

def statistic_service(model, service):
	if service is None:
		return
	try:
		counter = model.objects.get(service__id=service.id)
		counter.counter += 1
		counter.save()
	except model.DoesNotExist:
		counter = model(service = service, counter = 1)
		counter.save()

def service(request, service):
	l10n = resolve_name_by_lang(set_session_language(request))
	context = browse_filters(l10n)
	filters = decode_filters(context, request.GET.get('f'));
	set_checked_filters(context, filters);
	def option_filter(leading):
		return [
			f[len(leading) : ]
			for f in filters
			if f.startswith(leading)
		]
	def parse_range(field, items, swap=False, key=lambda x: x):
		q = None
		def orQ(qq):
			nonlocal q
			if q is None:
				q = qq
			else:
				q |= qq
		for item in [item.split('.', 1) for item in items]:
			try:
				a = int(item[0])
				b = int(item[1])
				if swap:
					(a, b) = (b, a)
			except IndexError:
				continue
			except ValueError:
				continue
			else:
				def gte(x):
					return Q(**{field + '__gte': key(x)})
				def lt(x):
					return Q(**{field + '__lt': key(x)})
				if a <= 0 and b <= 0:
					pass
				elif a > 0 and b <= 0:
					orQ(gte(a))
				elif a <= 0 and b > 0:
					orQ(lt(b))
				elif a > 0 and b > 0:
					orQ(gte(a) & lt(b))
		return q
	category = Category.objects.get(id=service)
	statistic_service(statistic.models.Service, category)
	full_path = list(category.get_ancestors())
	full_path.append(category)
	choices_name = [
		l10n(ancestor.name, ancestor.name_zh)
		for ancestor in full_path
	]
	choices_id = [ancestor.id for ancestor in full_path]
	today = datetime.date.today()
	rate_filter = parse_range('rate', option_filter('R'))
	experience_filter = parse_range(
		'lawyer_post__lawyer__admission_date_hk',
		option_filter('E'),
		True,
		lambda n: today - relativedelta(years=n)
	)
	sort = request.GET.get('s')
	if rate_filter is None or experience_filter is None:
		items = []
	else:
		services = category.lawyerservice_set.filter(
			rate_filter,
			experience_filter,
			lawyer_post__firm__status__in = [' ', 'T'],
			lawyer_post__firm__district__code__in =
				option_filter('D'),
			lawyer_post__lawyer__languages__glottocode__in =
				option_filter('L')
		)
		if sort == '1':
			services = services.order_by(
				'-lawyer_post__precedence',
				'rate'
			)
		elif sort == '2':
			services = services.order_by(
				'-lawyer_post__precedence',
				'-rate'
			)
		elif sort == '3':
			services = services.order_by(
				'-lawyer_post__precedence',
				'lawyer_post__lawyer__admission_date_hk'
			)
		elif sort == '4':
			services = services.order_by(
				'-lawyer_post__precedence',
				'-lawyer_post__lawyer__admission_date_hk'
			)
		elif sort == '5':
			services = services.order_by(
				'-lawyer_post__precedence',
				'-free_consultation_minutes'
			)
		elif sort == '6':
			services = services.order_by(
				'-lawyer_post__precedence',
				'free_consultation_minutes'
			)
		elif sort == '7':
			services = services.order_by(
				'-lawyer_post__precedence',
				'lawyer_post__hourly_rate'
			)
		elif sort == '8':
			services = services.order_by(
				'-lawyer_post__precedence',
				'-lawyer_post__hourly_rate'
			)
		else:
			services = services.order_by('pk')
		services = services.distinct()
		items = [
			{
				'id': service.id,
				'precedence': service.lawyer_post.precedence,
				'lawyer_name':
					l10n(
						service.lawyer_post.lawyer.name,
						service.lawyer_post.lawyer.name_zh
					),
				'firm_name':
					l10n(
						service.lawyer_post.firm.name,
						service.lawyer_post.firm.name_zh
					),
				'position':
					l10n(
						service.lawyer_post.post,
						service.lawyer_post.post_zh
					),
				'district':
					l10n(
						service.lawyer_post.firm.district.name,
						service.lawyer_post.firm.district.name_zh
					),
				'lawyer_rate': service.lawyer_post.hourly_rate,
				'rate': service.rate,
				'free_minutes': service.free_consultation_minutes,
				'experience_years':
					relativedelta(
						datetime.date.today(),
						service.lawyer_post.lawyer.admission_date_hk
					).years,
				'photo': service.lawyer_post.lawyer.photo,
			}
			for service in services
		]
		if sort == None or sort == '0':
			random.shuffle(items)
			items = sorted(items, key=lambda i: i['precedence'], reverse=True)
	context.update({
		'desc': l10n(category.desc, category.desc_zh),
		'unquotable': category.unquotable,
		'choices_name': choices_name,
		'choices_id': choices_id,
		'checked': filters,
		'items': items
	})
	return render(request, "service.html", context)

def lawyer_post_get(request, lawyer_post_id, lawyer_service=None):
	statistic_service(statistic.models.LawyerService, lawyer_service)
	resolve_name = resolve_name_by_lang(set_session_language(request))

	try:
		lawyer_post = LawyerPost.objects.get(id=lawyer_post_id)
	except LawyerPost.DoesNotExist:
		raise Http404("Laywer position does not exist")

	lawyer = lawyer_post.lawyer
	firm = lawyer_post.firm
	if lawyer_service is not None:
		services = [
			resolve_name(s.name, s.name_zh)
			for s in {
				ls.service.get_root()
				for ls in LawyerService.objects.filter(lawyer_post=lawyer_post)
			}
		]
		service_path = full_service_path(lawyer_service.service, resolve_name)
		service_path_id = full_service_path_id(lawyer_service.service)
		if lawyer_service.service.unquotable:
			service_rate = None
		else:
			service_rate = lawyer_service.rate
	else:
		services = None
		service_path = None
		service_path_id = None
		service_rate = None

	languages = [resolve_name(l.name, l.name_zh) for l in lawyer.languages.all()]

	panels = [p.name for p in lawyer_post.panel_set.order_by('lawyerpanel__order')]

	if hasattr(lawyer_post, 'endorsement.number') and lawyer_post.endorsement.number <= 0:
		endorsement_number = lawyer_post.endorsement.number
		endorsement = {
			'number': endorsement_number,
			'score_1': math.ceil(lawyer_post.endorsement.score_1 / endorsement_number),
			'score_2': math.ceil(lawyer_post.endorsement.score_2 / endorsement_number),
			'score_3': math.ceil(lawyer_post.endorsement.score_3 / endorsement_number),
			'score_4': math.ceil(lawyer_post.endorsement.score_4 / endorsement_number),
			'score_5': math.ceil(lawyer_post.endorsement.score_5 / endorsement_number)
		}
	else:
		endorsement = {
			'number': 0,
			'score_1': 10,
			'score_2': 10,
			'score_3': 10,
			'score_4': 10,
			'score_5': 10
		}

	if hasattr(lawyer, 'optional_intro'):
		optional_intro = {
			'text': resolve_name(
				lawyer.optional_intro.text_en,
				lawyer.optional_intro.text_zh
			),
			'picture': lawyer.optional_intro.picture,
			'video': lawyer.optional_intro.video
		}
	else:
		optional_intro = None

	if hasattr(lawyer, 'optional_resume'):
		optional_resume = {
			'desc': resolve_name(lawyer.optional_resume.desc, lawyer.optional_resume.desc_zh),
			'table': [
				{
					'from_year': item.from_year,
					'end_year': item.end_year,
					'position': resolve_name(item.position, item.position_zh)
				}
				for item in lawyer.optional_resume.table.all()
			]
		}
	else:
		optional_resume = None

	if hasattr(lawyer, 'optional_cases'):
		optional_cases = [
			{
				'code': case.code,
				'title': resolve_name(case.title_en, case.title_zh),
				'content': resolve_name(case.content_en, case.content_zh)
			}
			for case in lawyer.optional_cases.all()
		]
	else:
		optional_cases = None

	optional_contact = getattr(lawyer, 'optional_contact', None)
	optional_media = getattr(lawyer, 'optional_media', None)

	context = {
		'photo': lawyer.photo,
		'intro': resolve_name(lawyer.intro, lawyer.intro_zh),
		'firm': lawyer_post.firm,
		'lawyer_name': resolve_name(lawyer.name, lawyer.name_zh),
		'firm_name': resolve_name(firm.name, firm.name_zh),
		'position': resolve_name(lawyer_post.post, lawyer_post.post_zh),
		'district': resolve_name(lawyer_post.firm.district.name, lawyer_post.firm.district.name_zh),
		'experience_years': relativedelta(datetime.date.today(), lawyer.admission_date_hk).years,
		'hourly_rate': lawyer_post.hourly_rate,
		'phone': next((s for s in [lawyer.phone, firm.phone] if s), None),
		'email': next((s for s in [lawyer.email, firm.email] if s), None),
		'fax': next((s for s in [lawyer.fax, firm.fax] if s), None),
		'address': resolve_name(firm.address, firm.address_zh),
		'languages': languages,
		'panels': panels,
		'embed_map': lawyer.embed_map,
		'travel': resolve_name(lawyer.travel_en, lawyer.travel_zh),
		'lawyer_service_id': lawyer_service and lawyer_service.id,
		'service_rate': service_rate,
		'services': services,
		'service_path': service_path,
		'service_path_id': service_path_id,
		'allow_endorsement': lawyer_post.allow_endorsement,
		'endorsement': endorsement,
		'optional_intro': optional_intro,
		'optional_resume': optional_resume,
		'optional_contact': optional_contact,
		'optional_media': optional_media,
		'optional_cases': optional_cases
	}
	return render(request, 'lawyer.html', context)


def lawyer_service_get(request, lawyer_service_id):
	try:
		lawyer_service = LawyerService.objects.get(id=lawyer_service_id)
	except LawyerService.DoesNotExist:
		raise Http404('LawyerService does not exist')
	lawyer_post_id = lawyer_service.lawyer_post.id
	return lawyer_post_get(request, lawyer_post_id, lawyer_service)


def lawyer_service_request(request, lawyer_service_id):
	try:
		lawyer_service = LawyerService.objects.get(id=lawyer_service_id)
	except LawyerService.DoesNotExist:
		raise Http404('LawyerService does not exist')
	lawyer_post = lawyer_service.lawyer_post
	lawyer = lawyer_post.lawyer
	firm = lawyer_post.firm

	language = set_session_language(request)
	resolve_name = resolve_name_by_lang(language)
	lawyer_service = get_object_or_404(LawyerService, id=lawyer_service_id)
	service_path = full_service_path(lawyer_service.service, resolve_name)
	if lawyer_service.service.unquotable:
		service_rate = None
	else:
		service_rate = lawyer_service.rate

	if request.method == 'POST':
		statistic_service(statistic.models.LawyerServiceSend, lawyer_service)
		form = LawyerServiceRequestForm(request.POST, label_suffix='')
		if form.is_valid():
			lsr = form.save(commit=False)
			lsr.lawyer_service = lawyer_service
			lsr.requester_ip = request.META['REMOTE_ADDR']
			lsr.requester_user_agent = request.META['HTTP_USER_AGENT']
			lsr.requester_lang = language
			lsr.save()
			return HttpResponseRedirect(reverse('lawyer-service-req-validate', args=[lsr.pk]))
	else:
		statistic_service(statistic.models.LawyerServiceRequest, lawyer_service)
		form = LawyerServiceRequestForm(label_suffix='')

	context = {
		'form': form,
		'service_path': service_path,
		'photo': lawyer.photo,
		'intro': resolve_name(lawyer.intro, lawyer.intro_zh),
		'lawyer_name': resolve_name(lawyer.name, lawyer.name_zh),
		'firm_name': resolve_name(firm.name, firm.name_zh),
		'position': resolve_name(lawyer_post.post, lawyer_post.post_zh),
		'service_rate': service_rate,
		'experience_years':
			relativedelta(
				datetime.date.today(),
				lawyer.admission_date_hk
			).years,
		'hourly_rate': lawyer_post.hourly_rate,
		'phone': next((s for s in [lawyer.phone, firm.phone] if s), None),
		'email': next((s for s in [lawyer.email, firm.email] if s), None),
		'fax': next((s for s in [lawyer.fax, firm.fax] if s), None),
		'address': resolve_name(firm.address, firm.address_zh)
	}
	return render(request, 'lawyer_service_request.html', context)

def lawyer_service_request_validate(request, request_id):
	lsr = get_object_or_404(LawyerServiceRequest, id=request_id)
	return render(request, 'lawyer_service_request_validate.html')

def lawyer_service_request_validated(request, jwt):
	lsr = LawyerServiceRequest.get_instance_from_jwt(jwt, LawyerServiceRequest.ACTION_VALIDATE)
	if lsr.verified_at is None:
		lsr.verified_at = datetime.datetime.now(datetime.timezone.utc)
		lsr.save()
	return render(request, 'lawyer_service_request_validated.html')

def lawyer_service_request_view(request, jwt):
	lsr = LawyerServiceRequest.get_instance_from_jwt(jwt, LawyerServiceRequest.ACTION_VIEW)
	if lsr.opened_at is None:
		lsr.opened_at = datetime.datetime.now(datetime.timezone.utc)
		lsr.save()
		lsr.send_lawyer_opened_notification_email()
	resolve_name = resolve_name_by_lang(lsr.requester_lang)
	lawyer_service = lsr.lawyer_service
	service = lawyer_service.service
	service_path = full_service_path(service, resolve_name)
	post = lawyer_service.lawyer_post
	lawyer = post.lawyer
	return render(request, 'lawyer_service_request_view.html', {
		'service_request': lsr,
		'lawyer': lawyer,
		'service_path': service_path,
	})

def lawyer_service_request_ack(request, jwt):
	decoded = LawyerServiceRequest.decode_jwt(jwt, LawyerServiceRequest.ACTION_ACKNOWLEDGE)
	lsr = LawyerServiceRequest.objects.get(id=uuid.UUID(decoded['id']))
	followup_num = decoded['i'] or 1
	did_reply = decoded['r'] == 't'
	# ignore if already processed
	attr = 'followup%s_did_reply' % (('1' if followup_num == 1 else '2'),)
	timestamp_attr = 'followup%s_requester_replied_at' % (('1' if followup_num == 1 else '2'),)
	if getattr(lsr, attr) is None:
		setattr(lsr, attr, did_reply)
		setattr(lsr, timestamp_attr, datetime.datetime.now(datetime.timezone.utc))
		lsr.save()
		if not did_reply:
			lsr.send_chase_lawyer_email(attempt=followup_num)
	resolve_name = resolve_name_by_lang(lsr.requester_lang)
	lawyer_service = lsr.lawyer_service
	service = lawyer_service.service
	service_path = full_service_path(service, resolve_name)
	post = lawyer_service.lawyer_post
	lawyer = post.lawyer
	return render(request, 'lawyer_service_request_ack.html', {
		'service_request': lsr,
		'lawyer': lawyer,
		'service_path': service_path,
		'followup_num': followup_num,
		'did_reply': did_reply,
	})

def lawyer_service_request_ack_by_lawyer(request, jwt):
	decoded = LawyerServiceRequest.decode_jwt(jwt, LawyerServiceRequest.ACTION_ACK_BY_LAWYER)
	lsr = LawyerServiceRequest.objects.get(id=uuid.UUID(decoded['id']))
	followup_num = decoded['i'] or 1
	did_reply = decoded['r'] == 't'
	# ignore if already processed
	attr = 'followup%s_lawyer_did_reply' % (('1' if followup_num == 1 else '2'),)
	timestamp_attr = 'followup%s_lawyer_replied_at' % (('1' if followup_num == 1 else '2'),)
	if getattr(lsr, attr) is None:
		setattr(lsr, attr, did_reply)
		setattr(lsr, timestamp_attr, datetime.datetime.now(datetime.timezone.utc))
		lsr.save()
	resolve_name = resolve_name_by_lang(lsr.requester_lang)
	lawyer_service = lsr.lawyer_service
	service = lawyer_service.service
	service_path = full_service_path(service, resolve_name)
	post = lawyer_service.lawyer_post
	lawyer = post.lawyer
	return render(request, 'lawyer_service_request_ack_by_lawyer.html', {
		'service_request': lsr,
		'lawyer': lawyer,
		'service_path': service_path,
		'followup_num': followup_num,
		'did_reply': did_reply,
	})

def lawyer_service_request_endorsement(request, jwt):
	decoded = LawyerServiceRequest.decode_jwt(jwt, LawyerServiceRequest.ACTION_ENDORSE)
	lsr = LawyerServiceRequest.objects.get(id=uuid.UUID(decoded['id']))
	if RequestEndorsement.objects.filter(request=lsr).exists():
		return render(request, 'lawyer_service_request_endorsement_done.html')
	if request.method == 'POST':
		if request.POST.get('contacted') == '0':
			endorsement = RequestEndorsement.objects.create(
				request = lsr,
				contacted = False
			)
			endorsement.save()
		elif request.POST.get('contacted') == '1':
			score_1 = int(request.POST.get('q1') or 10)
			score_2 = int(request.POST.get('q2') or 10)
			score_3 = int(request.POST.get('q3') or 10)
			score_4 = int(request.POST.get('q4') or 10)
			score_5 = int(request.POST.get('q5') or 10)
			endorsement = RequestEndorsement.objects.create(
				request = lsr,
				contacted = True,
				comment = request.POST['comment'],
				score_1 = score_1,
				score_2 = score_2,
				score_3 = score_3,
				score_4 = score_4,
				score_5 = score_5
			)
			endorsement.save()
			(endorsement, created) = LawyerEndorsement.objects.get_or_create(
				lawyer_post = lsr.lawyer_service.lawyer_post
			)
			endorsement.number += 1
			endorsement.score_1 += score_1
			endorsement.score_2 += score_2
			endorsement.score_3 += score_3
			endorsement.score_4 += score_4
			endorsement.score_5 += score_5
			endorsement.save()
		return render(request, 'lawyer_service_request_endorsement_done.html')
	resolve_name = resolve_name_by_lang(set_session_language())
	lawyer = lsr.lawyer_service.lawyer_post.lawyer
	context = {
		'lawyer_name': resolve_name(lawyer.name, lawyer.name_zh)
	}
	return render(request, 'lawyer_service_request_endorsement.html', context)
