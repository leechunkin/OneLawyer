from datetime import date, datetime, timezone, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.core.mail import send_mail
from legitbase.models import LawyerServiceRequest

DEADLINE = timedelta(weeks=2)

class Command(BaseCommand):
	help = 'Send followup emails to pending requests'

	def handle(self, *args, **options):
		# get all requests with:
		# - sent_at more than 2 weeks ago but no followup1_at
		# - followup1_at more than 2 weeks ago, followup1_did_reply not True, followup1_lawyer_did_reply not True, no followup2_at
		deadline = datetime.now(timezone.utc) - DEADLINE
		crit1 = Q(sent_at__lte=deadline) & Q(followup1_at__exact=None)
		crit2 = Q(followup1_at__lte=deadline) & ~Q(followup1_did_reply__exact=True) & ~Q(followup1_lawyer_did_reply__exact=True) & Q(followup2_at__exact=None)
		qs = LawyerServiceRequest.objects.filter(crit1 | crit2)
		for lsr in qs:
			state = lsr.resolve_state()
			if state == LawyerServiceRequest.STATE_NEED_SEND_FOLLOWUP_1 or state == LawyerServiceRequest.STATE_NEED_SEND_FOLLOWUP_2:
				attempt = 1 if state == LawyerServiceRequest.STATE_NEED_SEND_FOLLOWUP_1 else 2
				try:
					lsr.send_followup_email(attempt)
				except smtplib.SMTPException:
					pass
