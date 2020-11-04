from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.utils.safestring import mark_safe
from django.utils import translation
from .models import BasicPage


def resolve_name_by_lang(request):
	lang = translation.get_language() or 'zh'
	if lang.startswith('zh'):
		lang = 'zh'
	else:
		lang = 'en'
	translation.activate(lang)
	if hasattr(request, 'session'):
		request.session[translation.LANGUAGE_SESSION_KEY] = lang

	def resolve_name_zh(name_en, name_zh):
		return name_zh or name_en
	def resolve_name_en(name_en, name_zh):
		return name_en or name_zh

	if lang == 'zh':
		return resolve_name_zh
	else:
		return resolve_name_en


def basicpage(request, url):
	if not url.startswith('/'):
		url = '/' + url
	try:
		p = get_object_or_404(BasicPage, url=url)
	except Http404:
		if not url.endswith('/'):
			url += '/'
			p = get_object_or_404(BasicPage, url=url)
			return HttpResponsePermanentRedirect('%s/' % request.path)
		else:
			raise

	resolve_name = resolve_name_by_lang(request)
	title = resolve_name(p.title, p.title_zh)
	content = resolve_name(p.content, p.content_zh)
	return render(request, 'content/basicpage.html', context={
		'url': url,
		'title': mark_safe(title),
		'content': mark_safe(content),
	})
