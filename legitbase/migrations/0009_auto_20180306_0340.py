# Generated by Django 2.0.2 on 2018-03-06 03:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0008_category_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cannotquote',
            name='category',
            field=models.OneToOneField(limit_choices_to={'numchild': 0}, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='legitbase.Category'),
        ),
    ]
