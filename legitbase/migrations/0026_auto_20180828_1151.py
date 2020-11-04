# Generated by Django 2.0.3 on 2018-08-28 11:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('legitbase', '0025_optionalintro'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lawyerpost',
            options={'permissions': (('admin_lawyer', 'Lawyer Admin: Can only change own lawyer'),), 'verbose_name': 'Lawyer Post', 'verbose_name_plural': 'Lawyer Posts'},
        ),
        migrations.AddField(
            model_name='lawyerpost',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lawyer_admins', to=settings.AUTH_USER_MODEL, verbose_name='Admin account of lawyer'),
        ),
    ]