import uuid
import jwt
from datetime import date, datetime, timedelta, timezone
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from treebeard.mp_tree import MP_Node
from ordered_model.models import OrderedModel
from .utils import resolve_name_by_lang, send_mail

class Category(MP_Node):
	id = models.AutoField(primary_key=True)
	name = models.CharField(_('Name (English)'), max_length=80)
	name_zh = models.CharField(_('Name (Chinese)'), max_length=80, blank=True)
	desc = models.TextField(_('Description (English)'), blank=True)
	desc_zh = models.TextField(_('Description (Chinese)'), blank=True)
	unquotable = models.BooleanField(_('Unquotable'), default=False)
	order = models.PositiveSmallIntegerField(_('Order'), default=0)

	node_order_by = ['order']

	def __str__(self):
		parent = self.get_parent()
		if parent is not None:
			return parent.__str__() + ' > ' + self.name
		return self.name

	def get_absolute_url(self):
		return reverse('service', args=[str(self.id)]) + '?select=all'

	class Meta:
		verbose_name = _('Category')
		verbose_name_plural = _('Categories')


class LawFirm(models.Model):
	LAWFIRM_STATUSES = (
		('X', _('Invalid')),
		('T', _('Free Trial')),
		(' ', _('Normal')),
		('!', _('Not Paying')),
	)
	id = models.AutoField(primary_key=True)
	name = models.CharField(_('Name (English)'), max_length=255)
	name_zh = models.CharField(_('Name (Chinese)'), max_length=255, blank=True)
	address = models.TextField(_('Address (English)'))
	address_zh = models.TextField(_('Address (Chinese)'), blank=True)
	district = models.ForeignKey('HKDistrict', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('HK District'))
	email = models.EmailField(_('Email'), blank=True, null=True)
	phone = models.CharField(_('Phone'), max_length=255, blank=True)
	fax = models.CharField(_('Fax'), max_length=255, blank=True)
	website = models.URLField(_('Website'), blank=True, null=True)
	lawsochk_profile = models.URLField(_('hklawsoc.org.hk Profile URL'), blank=True, null=True)

	remarks = models.TextField(_('Remarks'), blank=True)
	status = models.CharField(_('Status'), max_length=1, choices=LAWFIRM_STATUSES, default=' ')
	subscription_start_date = models.DateField(_('Subscription Starts'), blank=True, null=True)
	subscription_end_date = models.DateField(_('Subscription Ends'), blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	subscription_nag_sent = models.DateTimeField(blank=True, null=True)

	admins = models.ManyToManyField(User, related_name='lawfirm_admins', blank=True, verbose_name=_('Law Firm Admins'))

	def __str__(self):
		return '%s %s' % (self.name_zh, self.name)

	class Meta:
		verbose_name = _('Law Firm')
		verbose_name_plural = _('Law Firms')
		permissions = (
			# users with admin_firm cannot change 'remarks', 'status' and 'admins'
			('admin_firm', _('Law Firm Admin: Can only change own law firm')),
		)


class Lawyer(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(_('Name (English)'), max_length=255)
	name_zh = models.CharField(_('Name (Chinese)'), max_length=255, blank=True)
	admission_date_hk = models.DateField(_('Admission in Hong Kong'), blank=True, null=True)
	jurisdictions = models.ManyToManyField('Jurisdiction', through='LawyerJurisdiction', verbose_name=_('Jurisdictions'))
	email = models.EmailField(_('Email'), blank=True, null=True)
	phone = models.CharField(_('Phone'), max_length=255, blank=True)
	fax = models.CharField(_('Fax'), max_length=255, blank=True)
	lawsochk_profile = models.URLField(_('hklawsoc.org.hk Profile URL'), blank=True, null=True)
	languages = models.ManyToManyField('Language', verbose_name=_('Languages'))

	firms = models.ManyToManyField(LawFirm, through='LawyerPost', verbose_name=_('Firms'))

	intro = models.TextField(_('Introduction (English)'), blank=True)
	intro_zh = models.TextField(_('Introduction (Chinese)'), blank=True)
	embed_map = models.TextField('map', null=True, blank=True)
	travel_en = models.TextField('Travel (English)', blank=True)
	travel_zh = models.TextField('Travel (Chinese)', blank=True)
	remarks = models.TextField(_('Remarks'), blank=True)

	photo = models.ImageField(_('Photo'), upload_to='lawyer/photo/', blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '%s %s' % (self.name_zh, self.name)

	class Meta:
		verbose_name = _('Lawyer')
		verbose_name_plural = _('Lawyers')


class Jurisdiction(models.Model):
	jurisdiction = models.CharField(_('Jurisdiction'), max_length=255)

	def __str__(self):
		return self.jurisdiction

	class Meta:
		verbose_name = _('Jurisdiction')
		verbose_name_plural = _('Jurisdictions')


class LawyerJurisdiction(models.Model):
	lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, verbose_name=_('Lawyer'))
	jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.CASCADE, verbose_name=_('Jurisdiction'))
	admission_date = models.DateField(_('Admission Date'))

	class Meta:
		verbose_name = _('Lawyer Jurisdiction')
		verbose_name_plural = _('Lawyer Jurisdictions')


class LawyerPost(models.Model):
	firm = models.ForeignKey(LawFirm, on_delete=models.CASCADE, verbose_name=_('Firm'))
	lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, verbose_name=_('Lawyer'))

	post = models.CharField(_('Post (English)'), max_length=255)
	post_zh = models.CharField(_('Post (Chinese)'), max_length=255, blank=True)

	from_date = models.DateField(_('From Date'), help_text=_('Date from which this position begins.'))
	end_date = models.DateField(_('End Date'), help_text=_('Date on which this position ends. Leave blank if position is current.'), blank=True, null=True)

	hourly_rate = models.PositiveIntegerField(_('Hourly Rate'), help_text=_('in HKD'), default=0)

	precedence = models.PositiveSmallIntegerField(_('Precedence to show in service list'), default=0)
	services = models.ManyToManyField(Category, through='LawyerService')

	allow_endorsement = models.BooleanField('Allow endorsement', default=False)

	admin = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='lawyer_admins', verbose_name='Admin account of lawyer')

	class Meta:
		verbose_name = _('Lawyer Post')
		verbose_name_plural = _('Lawyer Posts')
		permissions = (
			('admin_lawyer', _('Lawyer Admin: Can only change own lawyer')),
		)

	def __str__(self):
		return '%s @ %s' % (self.lawyer.__str__(), self.firm.__str__())
	

class LawyerService(models.Model):
	FREE_CHOICES = (
		(0, _('None')),
		(15, _('Under 15 Minutes')),
		(30, _('15-30 Minutes')),
		(1000000, _('30 Minutes or more')),
	)
	service = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'numchild': 0}, verbose_name=_('Service'))
	lawyer_post = models.ForeignKey(LawyerPost, on_delete=models.CASCADE, verbose_name=_('Lawyer Post'))
	rate = models.PositiveIntegerField(_('Rate'), default=0)
	is_hourly_rate = models.BooleanField(_('Hourly Rate?'), default=False)
	time_estimate_minutes_max = models.PositiveIntegerField(_('Max Estimated Time (minutes)'), default=0)
	free_consultation_minutes = models.PositiveIntegerField(_('Free Consultation Offer (minutes)'), default=0, choices=FREE_CHOICES)

	def __str__(self):
		return '%s : %s' % (self.lawyer_post.__str__(), self.service.__str__())

	def get_absolute_url(self):
		return reverse('lawyer-service', args=[str(self.id)])

	class Meta:
		verbose_name = _('Lawyer Service')
		verbose_name_plural = _('Lawyer Services')


class Panel(models.Model):
	name = models.CharField('Name', primary_key=True, max_length=80)
	lawyer_post = models.ManyToManyField(LawyerPost, through='LawyerPanel')
	def __str__(self):
		return self.name

class LawyerPanel(OrderedModel):
	lawyer_post = models.ForeignKey(
		LawyerPost,
		on_delete=models.CASCADE,
		verbose_name=_('Lawyer Post')
	)
	panel = models.ForeignKey(
		Panel,
		on_delete=models.CASCADE,
		verbose_name=_('Panel')
	)
	order_with_respect_to = 'lawyer_post'
	class Meta(OrderedModel.Meta):
		ordering = ['lawyer_post', 'order']


class HKDistrict(models.Model):
	# see http://www.xml.gov.hk/en/approved/structured_address_v1_0.htm for codes
	REGIONS = (
		('HK', _('Hong Kong')),
		('KLN', _('Kowloon')),
		('NT', _('New Territories')),
	)
	code = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(_('Name (English)'), max_length=255)
	name_zh = models.CharField(_('Name (Chinese)'), max_length=255)
	region = models.CharField(_('Region'), max_length=3, choices=REGIONS)

	def __str__(self):
		return '%s %s' % (self.name_zh, self.name)

	class Meta:
		verbose_name = _('HK District')
		verbose_name_plural = _('HK Districts')
		ordering = ['region', 'code']


class Language(models.Model):
	glottocode = models.CharField('Glottocode', primary_key=True, max_length=8)
	iso639_3 = models.CharField('ISO 639-3 Code', max_length=3, blank=True)
	name = models.CharField(_('Name (English)'), max_length=255)
	name_zh = models.CharField(_('Name (Chinese)'), max_length=255, blank=True)

	def __str__(self):
		return '%s %s' % (self.name_zh, self.name)

	class Meta:
		verbose_name = _('Language')
		verbose_name_plural = _('Languages')
		ordering = ['glottocode']


class Experience(models.Model):
	yearFrom = models.PositiveIntegerField('Above or equal')
	yearTo = models.PositiveIntegerField('Less than')
	desc = models.CharField('Description (English)', max_length=255)
	desc_zh = models.CharField('Description (Chinese)', max_length=255)
	class Meta:
		ordering = ['yearFrom']

class ItemRate(models.Model):
	rateFrom = models.PositiveIntegerField('Above or equal')
	rateTo = models.PositiveIntegerField('Less than')
	desc = models.CharField('Description (English)', max_length=255)
	desc_zh = models.CharField('Description (Chinese)', max_length=255)
	class Meta:
		ordering = ['rateFrom']

class OptionalIntro(models.Model):
	lawyer = models.OneToOneField(Lawyer, primary_key=True, on_delete=models.CASCADE, related_name='optional_intro')
	text_en = models.TextField('Introduction (English)', blank=True)
	text_zh = models.TextField('律師介紹 (中文)', blank=True)
	picture = models.ImageField('Picture', upload_to='lawyer/optional/', null=True, blank=True)
	video = models.FileField('Video', upload_to='lawyer/optional/', null=True, blank=True)
	def __str__(self):
		return str(self.lawyer)

class OptionalResume(models.Model):
	lawyer = models.OneToOneField(Lawyer, primary_key=True, on_delete=models.CASCADE, related_name='optional_resume')
	desc = models.TextField('Description (English)', blank=True)
	desc_zh = models.TextField('敍述 (中文)', blank=True)
	def __str__(self):
		return str(self.lawyer)

class OptionalResumeEntry(models.Model):
	resume = models.ForeignKey(OptionalResume, on_delete=models.CASCADE, related_name='table')
	from_year = models.PositiveSmallIntegerField('From Year')
	end_year = models.PositiveSmallIntegerField('End Year', null=True, blank=True)
	position = models.CharField('Position', max_length=255, blank=True)
	position_zh = models.CharField('職位 (中文)', max_length=255, blank=True)
	class Meta:
		ordering = ['-from_year']

class OptionalContact(models.Model):
	lawyer = models.OneToOneField(Lawyer, primary_key=True, on_delete=models.CASCADE, related_name='optional_contact')
	text = models.TextField(blank=True)
	picture = models.ImageField(null=True, blank=True, upload_to='lawyer/optional/')
	video = models.FileField(null=True, blank=True, upload_to='lawyer/optional/')
	def __str__(self):
		return str(self.lawyer)

class OptionalMedia(models.Model):
	lawyer = models.OneToOneField(Lawyer, primary_key=True, on_delete=models.CASCADE, related_name='optional_media')
	text = models.TextField(blank=True)
	picture = models.ImageField(null=True, blank=True, upload_to='lawyer/optional/')
	video = models.FileField(null=True, blank=True, upload_to='lawyer/optional/')
	class Meta:
		verbose_name_plural = 'optional media'
	def __str__(self):
		return str(self.lawyer)

class OptionalCase(OrderedModel):
	lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='optional_cases')
	code = models.CharField('Court Case Number', max_length=20, blank=True)
	title_en = models.CharField('Title', max_length=255, blank=True)
	title_zh = models.CharField('標題', max_length=255, blank=True)
	content_en = models.TextField('Content', blank=True)
	content_zh = models.TextField('內文', blank=True)
	class Meta(OrderedModel.Meta):
		pass
	def __str__(self):
		return self.code + ': ' + (self.title_en or self.title_zh)

class LawyerServiceRequest(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	lawyer_service = models.ForeignKey(LawyerService, on_delete=models.SET_NULL, null=True)
	requester_name = models.CharField(_('Name'), max_length=255)
	requester_email = models.EmailField(_('Email'))
	requester_phone = models.CharField(_('Phone'), max_length=255)
	message = models.TextField(_('Brief summary of this consultation'))
	time_choice1 = models.DateTimeField(_('First choice'), blank=True, null=True)
	time_choice2 = models.DateTimeField(_('Second choice'), blank=True, null=True)
	time_choice3 = models.DateTimeField(_('Third choice'), blank=True, null=True)
	requested_at = models.DateTimeField(auto_now_add=True)
	requester_ip = models.GenericIPAddressField()
	requester_user_agent = models.TextField()
	requester_lang = models.CharField(max_length=16)
	verified_at = models.DateTimeField(blank=True, null=True)
	sent_at = models.DateTimeField(blank=True, null=True)
	opened_at = models.DateTimeField(blank=True, null=True)
	followup1_at = models.DateTimeField(blank=True, null=True)
	followup1_did_reply = models.NullBooleanField()
	followup1_lawyer_did_reply = models.NullBooleanField()
	followup1_requester_replied_at = models.DateTimeField(blank=True, null=True)
	followup1_lawyer_replied_at = models.DateTimeField(blank=True, null=True)
	followup2_at = models.DateTimeField(blank=True, null=True)
	followup2_did_reply = models.NullBooleanField()
	followup2_lawyer_did_reply = models.NullBooleanField()
	followup2_requester_replied_at = models.DateTimeField(blank=True, null=True)
	followup2_lawyer_replied_at = models.DateTimeField(blank=True, null=True)
	endorse_at = models.DateTimeField(blank=True, null=True)
	is_spam = models.BooleanField(default=False)

	STATE_NEED_VERIFY_EMAIL = 0
	STATE_NEED_SEND_REQUEST = 1
	STATE_SENT_REQUEST = 2
	STATE_NEED_SEND_FOLLOWUP_1 = 11
	STATE_SENT_FOLLOWUP_1 = 12
	STATE_FOLLOWUP_1_NACK_BY_REQUESTER = 13
	STATE_NEED_SEND_FOLLOWUP_2 = 21
	STATE_SENT_FOLLOWUP_2 = 22
	STATE_FOLLOWUP_2_NACK_BY_REQUESTER = 23
	STATE_FOLLOWUP_ACK_BY_REQUESTER = 81
	STATE_FOLLOWUP_ACK_BY_LAWYER = 82

	def resolve_state(self):
		now = datetime.now(timezone.utc)
		if self.verified_at is None:
			return self.STATE_NEED_VERIFY_EMAIL
		elif self.sent_at is None:
			return self.STATE_NEED_SEND_REQUEST
		elif self.followup1_did_reply == True or self.followup2_did_reply == True:
			return self.STATE_FOLLOWUP_ACK_BY_REQUESTER
		elif self.followup1_lawyer_did_reply == True or self.followup2_lawyer_did_reply == True:
			return self.STATE_FOLLOWUP_ACK_BY_LAWYER
		elif self.followup1_did_reply == False:
			return self.STATE_FOLLOWUP_1_NACK_BY_REQUESTER
		elif self.followup2_did_reply == False:
			return self.STATE_FOLLOWUP_2_NACK_BY_REQUESTER
		elif (now - self.sent_at) < timedelta(weeks=2):
			return self.STATE_SENT_REQUEST
		elif self.followup1_at is None:
			return self.STATE_NEED_SEND_FOLLOWUP_1
		elif (now - self.followup1_at) < timedelta(weeks=2):
			return self.STATE_SENT_FOLLOWUP_1
		elif self.followup2_at is None:
			return self.STATE_NEED_SEND_FOLLOWUP_2
		else:
			return self.STATE_SENT_FOLLOWUP_2

	def request_jwt(self, action, additional_context=None):
		context = {'id': str(self.id.hex), 'req': self.requester_email, 'a': action}
		if additional_context is not None:
			context.update(additional_context)
		return jwt.encode(
			context,
			settings.JWT_SECRET,
			algorithm=settings.JWT_ALGORITHM,
		)

	@classmethod
	def decode_jwt(cls, the_jwt, action=None):
		decoded = jwt.decode(the_jwt, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
		if (action is not None) and (not decoded['a'] == action):
			raise Exception('Action not match')
		return decoded

	@classmethod
	def get_instance_from_jwt(cls, the_jwt, action=None):
		decoded = cls.decode_jwt(the_jwt, action)
		return cls.objects.get(id=uuid.UUID(decoded['id']))

	@staticmethod
	def render_template(template_name, lang, context):
		return render_to_string('legitbase/email/%s.%s.txt' % (template_name, lang), context)

	def email_context(self, additional_context=None):
		resolve_name = resolve_name_by_lang(self.requester_lang)
		post = self.lawyer_service.lawyer_post
		context = {
			'request_id': str(self.id),
			'requester_name': self.requester_name,
			'lawyer_name': resolve_name(post.lawyer.name, post.lawyer.name_zh),
			'opened_at': self.opened_at,
			'requested_at': self.requested_at,
			'sent_at': self.sent_at,
		}
		if additional_context is not None:
			context.update(additional_context)
		return context

	ACTION_VALIDATE = 'val'
	def send_verify_email(self):
		translation.activate(self.requester_lang)
		the_jwt = self.request_jwt(self.ACTION_VALIDATE)
		the_url = settings.BASE_URL + reverse('lawyer-service-req-validated', args=[the_jwt.decode('utf-8')])
		send_mail(
			_('LEGIT: Please verify your request'),
			self.render_template('request_email_verify', self.requester_lang, {'verify_link': the_url}),
			[self.requester_email],
		)

	ACTION_VIEW = 'view'
	def send_lawyer_notification_email(self):
		translation.activate(self.requester_lang)
		the_jwt = self.request_jwt(self.ACTION_VIEW)
		the_url = settings.BASE_URL + reverse('lawyer-service-req-view', args=[the_jwt.decode('utf-8')])
		context = self.email_context({'the_url': the_url})
		send_mail(
			_('LEGIT: You have a new request! (ID: %s)') % (str(self.id),),
			self.render_template('request_notify_lawyer', self.requester_lang, context),
			[self.lawyer_service.lawyer_post.lawyer.email],
		)
		self.sent_at = datetime.now(timezone.utc)
		self.save()

	def send_lawyer_opened_notification_email(self):
		translation.activate(self.requester_lang)
		context = self.email_context()
		send_mail(
			_('LEGIT: Your request has been viewed by the lawyer'),
			self.render_template('request_opened', self.requester_lang, context),
			[self.requester_email],
		)

	ACTION_ACKNOWLEDGE = 'ack'
	def send_followup_email(self, attempt):
		translation.activate(self.requester_lang)
		resolve_name = resolve_name_by_lang(self.requester_lang)
		template_name = 'request_ack_confirm'
		if attempt == 1:
			subject = _('LEGIT: Request Follow-up')
			is_final = False
			timestamp_attr = 'followup1_at'
		else:
			subject = _('LEGIT: Final Requet Follow-up')
			is_final = True
			timestamp_attr = 'followup2_at'
		the_jwt_yes = self.request_jwt(self.ACTION_ACKNOWLEDGE, {'i': attempt, 'r': 't'})
		the_jwt_no = self.request_jwt(self.ACTION_ACKNOWLEDGE, {'i': attempt, 'r': 'f'})
		context = self.email_context({
			'yes_link': settings.BASE_URL + reverse('lawyer-service-req-ack', args=[the_jwt_yes.decode('utf-8')]),
			'no_link': settings.BASE_URL + reverse('lawyer-service-req-ack', args=[the_jwt_no.decode('utf-8')]),
			'is_final': is_final,
		})
		send_mail(
			subject,
			self.render_template(template_name, self.requester_lang, context),
			[self.requester_email],
		)
		setattr(self, timestamp_attr, datetime.now(timezone.utc))
		self.save()

	ACTION_ACK_BY_LAWYER = 'ack-by-lawyer'
	def send_chase_lawyer_email(self, attempt):
		translation.activate(self.requester_lang)
		resolve_name = resolve_name_by_lang(self.requester_lang)
		subject = _('LEGIT: Request Follow-up')
		template_name = 'request_chase_lawyer'
		the_jwt_yes = self.request_jwt(self.ACTION_ACK_BY_LAWYER, {'i': attempt, 'r': 't'})
		context = self.email_context({
			'yes_link': settings.BASE_URL + reverse('lawyer-service-req-ack-by-lawyer', args=[the_jwt_yes.decode('utf-8')]),
		})
		send_mail(
			subject,
			self.render_template(template_name, self.requester_lang, context),
			[self.lawyer_service.lawyer_post.lawyer.email],
		)

	ACTION_ENDORSE = 'endorse'
	def send_endorse_email(self):
		translation.activate(self.requester_lang)
		the_jwt = self.request_jwt(self.ACTION_ENDORSE)
		the_link = settings.BASE_URL + reverse('lawyer-service-req-endorsement', args=[the_jwt.decode('utf-8')])
		context = self.email_context({'the_link': the_link})
		send_mail(
			_('LEGIT: Please comment our service'),
			self.render_template('request_endorse', self.requester_lang, context),
			[self.requester_email],
		)
		self.endorse_at = datetime.now(timezone.utc)
		self.save()


class LawyerEndorsement(models.Model):
	lawyer_post = models.OneToOneField(LawyerPost, on_delete=models.CASCADE, primary_key=True, related_name='endorsement')
	number = models.PositiveIntegerField('Number of endorsements', default=0)
	score_1 = models.PositiveSmallIntegerField('Score of question 1', default=0)
	score_2 = models.PositiveSmallIntegerField('Score of question 2', default=0)
	score_3 = models.PositiveSmallIntegerField('Score of question 3', default=0)
	score_4 = models.PositiveSmallIntegerField('Score of question 4', default=0)
	score_5 = models.PositiveSmallIntegerField('Score of question 5', default=0)


class RequestEndorsement(models.Model):
	request = models.OneToOneField(LawyerServiceRequest, on_delete=models.CASCADE, primary_key=True)
	time = models.DateTimeField(auto_now_add=True)
	contacted = models.BooleanField()
	comment = models.TextField(blank=True)
	score_1 = models.PositiveSmallIntegerField(default=0)
	score_2 = models.PositiveSmallIntegerField(default=0)
	score_3 = models.PositiveSmallIntegerField(default=0)
	score_4 = models.PositiveSmallIntegerField(default=0)
	score_5 = models.PositiveSmallIntegerField(default=0)


@receiver(post_save, sender=LawyerServiceRequest)
def lawyer_service_request_post_save(sender, instance, **kwargs):
	state = instance.resolve_state()
	if state == LawyerServiceRequest.STATE_NEED_VERIFY_EMAIL:
		instance.send_verify_email()
	elif state == LawyerServiceRequest.STATE_NEED_SEND_REQUEST:
		instance.send_lawyer_notification_email()
