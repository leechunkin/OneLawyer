from datetime import date, datetime, timezone, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.core.mail import send_mail
from legitbase.models import LawyerServiceRequest

DELAY = timedelta(days=21)
DEADLINE = timedelta(days=28)

class Command(BaseCommand):
	help = 'Send endorse emails to requesters'

	def handle(self, *args, **options):
		delay = datetime.now(timezone.utc) - DELAY
		deadline = datetime.now(timezone.utc) - DEADLINE
		q = Q(sent_at__lte=delay) & Q(endorse_at__exact=None) & Q(lawyer_service__lawyer_post__allow_endorsement=True) & Q(sent_at__gte=deadline)
		qs = LawyerServiceRequest.objects.filter(q)
		for lsr in qs:
			try:
				lsr.send_endorse_email()
			except smtplib.SMTPException:
				pass
