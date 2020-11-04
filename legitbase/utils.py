from django.conf import settings
from django.core.mail import EmailMessage

def limit_number(n, minimum, maximum):
	if n < minimun:
		return minimum
	elif n > maximum:
		return maximum
	else:
		return n

def dict_pick(dictionary, fields):
	def pair(key):
		return (key, dictionary[key])
	return dict(map(pair, fields))

def dict_prefix(dictionary, prefix):
	def pickup(element):
		return element.startswith(prefix)
	def postfix(element):
		return element[len(prefix):]
	return dict(
		(postfix(key), dictionary[key])
		for key in dictionary.keys()
		if pickup(key)
	)

def resolve_name_by_lang(lang='zh'):
	def resolve_name(name_en, name_zh):
		if lang.startswith('zh'):
			names = [name_zh, name_en]
		else:
			names = [name_en, name_zh]
		if names[0]:
			return names[0]
		return names[1]
	return resolve_name

def send_mail(subject, body, recipient_list):
	email = EmailMessage(
		subject=subject,
		body=body,
		from_email=settings.MAIL_FROM,
		to=recipient_list,
		headers={'format': 'flowed'}
	)
	email.send()
