# Generated by Django 2.0.3 on 2018-09-09 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0030_auto_20180909_0436'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lawyerpanel',
            options={'ordering': ['lawyer_post', 'order']},
        ),
    ]