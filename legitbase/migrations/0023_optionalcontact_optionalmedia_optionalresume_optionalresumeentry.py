# Generated by Django 2.0.3 on 2018-08-27 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0022_auto_20180824_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionalContact',
            fields=[
                ('lawyer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='optional_contact', serialize=False, to='legitbase.Lawyer')),
                ('text', models.TextField(blank=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='lawyer/optional/')),
                ('video', models.FileField(blank=True, null=True, upload_to='lawyer/optional/')),
            ],
        ),
        migrations.CreateModel(
            name='OptionalMedia',
            fields=[
                ('lawyer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='optional_media', serialize=False, to='legitbase.Lawyer')),
                ('text', models.TextField(blank=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='lawyer/optional/')),
                ('video', models.FileField(blank=True, null=True, upload_to='lawyer/optional/')),
            ],
            options={
                'verbose_name_plural': 'optional media',
            },
        ),
        migrations.CreateModel(
            name='OptionalResume',
            fields=[
                ('lawyer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='optional_resume', serialize=False, to='legitbase.Lawyer')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='OptionalResumeEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_year', models.PositiveSmallIntegerField(verbose_name='From Year')),
                ('end_year', models.PositiveSmallIntegerField(verbose_name='End Year')),
                ('lawfirm', models.CharField(blank=True, max_length=255, verbose_name='Law Firm')),
                ('position', models.CharField(blank=True, max_length=255, verbose_name='Position')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table', to='legitbase.OptionalResume')),
            ],
            options={
                'ordering': ['-from_year'],
            },
        ),
    ]