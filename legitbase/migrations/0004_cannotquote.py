# Generated by Django 2.0.2 on 2018-02-26 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0003_auto_20180226_0510'),
    ]

    operations = [
        migrations.CreateModel(
            name='CannotQuote',
            fields=[
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='legitbase.Category')),
                ('message', models.TextField()),
                ('message_zh', models.TextField()),
            ],
        ),
    ]