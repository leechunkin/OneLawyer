# Generated by Django 2.0.3 on 2018-06-14 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0019_auto_20180612_0921'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yearFrom', models.PositiveIntegerField(verbose_name='Above or equal')),
                ('yearTo', models.PositiveIntegerField(verbose_name='Less than')),
                ('desc', models.CharField(max_length=255, verbose_name='Description (English)')),
                ('desc_zh', models.CharField(max_length=255, verbose_name='Description (Chinese)')),
            ],
            options={
                'ordering': ['yearFrom'],
            },
        ),
        migrations.CreateModel(
            name='ItemRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rateFrom', models.PositiveIntegerField(verbose_name='Above or equal')),
                ('rateTo', models.PositiveIntegerField(verbose_name='Less than')),
                ('desc', models.CharField(max_length=255, verbose_name='Description (English)')),
                ('desc_zh', models.CharField(max_length=255, verbose_name='Description (Chinese)')),
            ],
            options={
                'ordering': ['rateFrom'],
            },
        ),
    ]
