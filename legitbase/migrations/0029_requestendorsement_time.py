# Generated by Django 2.0.3 on 2018-09-08 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0028_auto_20180908_0526'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestendorsement',
            name='time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
