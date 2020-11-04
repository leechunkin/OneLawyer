# Generated by Django 2.0.3 on 2018-08-31 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0026_auto_20180828_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawyerEndorsement',
            fields=[
                ('lawyer_post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='endorsement', serialize=False, to='legitbase.LawyerPost')),
                ('number', models.PositiveIntegerField(default=0, verbose_name='Number of endorsements')),
                ('score_1', models.PositiveSmallIntegerField(default=0, verbose_name='Score of question 1')),
                ('score_2', models.PositiveSmallIntegerField(default=0, verbose_name='Score of question 2')),
                ('score_3', models.PositiveSmallIntegerField(default=0, verbose_name='Score of question 3')),
                ('score_4', models.PositiveSmallIntegerField(default=0, verbose_name='Score of question 4')),
                ('score_5', models.PositiveSmallIntegerField(default=0, verbose_name='Score of question 5')),
            ],
        ),
        migrations.CreateModel(
            name='RequestEndorsement',
            fields=[
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='legitbase.LawyerServiceRequest')),
                ('contacted', models.BooleanField()),
                ('comment', models.TextField(blank=True)),
                ('score_1', models.PositiveSmallIntegerField(default=0)),
                ('score_2', models.PositiveSmallIntegerField(default=0)),
                ('score_3', models.PositiveSmallIntegerField(default=0)),
                ('score_4', models.PositiveSmallIntegerField(default=0)),
                ('score_5', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='lawyerpost',
            name='allow_endorsement',
            field=models.BooleanField(default=False, verbose_name='Allow endorsement'),
        ),
        migrations.AddField(
            model_name='lawyerservicerequest',
            name='endorse_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]