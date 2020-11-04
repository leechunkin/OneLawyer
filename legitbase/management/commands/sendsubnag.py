from datetime import date, datetime, timezone, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.core.mail import send_mail
from legitbase.models import LawFirm

DEADLINE = timedelta(days=30)

class Command(BaseCommand):
	help = 'Send nag email to law firms whose subscriptions are ending'

	def handle(self, *args, **options):
		# get all firms with:
		# - subscription_end_date not null and less than 30 days away
		# - subscription_nag_sent null or more than 30 days before sub_end_date
		deadline = date.today() + DEADLINE
		qs = LawFirm.objects.filter(subscription_end_date__lte=deadline)
		qs = qs.filter(Q(subscription_nag_sent__exact=None) | Q(subscription_nag_sent__date__lt=F('subscription_end_date') - '30 days'))
		for firm in qs:
			admins = ['%s %s <%s>' % (a.first_name, a.last_name, a.email) for a in firm.admins.all()]
			if len(admins) == 0:
				raise Exception('LawFirm id:%d (%s) has no admins!' % (firm.id, firm.name))
			try:
				send_mail(
					'Your LEGIT Subscription is Ending!',
					'Your LEGIT subscription is ending! Please contact us!',
					'info@legit.express',
					admins,
				)
				firm.subscription_nag_sent = datetime.now(timezone.utc)
				firm.save()
			except smtplib.SMTPException:
				pass
