# Generated by Django 2.0.2 on 2018-03-01 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0007_merge_20180228_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]