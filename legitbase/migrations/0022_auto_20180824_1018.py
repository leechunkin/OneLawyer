# Generated by Django 2.0.3 on 2018-08-24 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legitbase', '0021_lawyerpost_precedence'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawyerPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order')),
                ('lawyer_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='legitbase.LawyerPost', verbose_name='Lawyer Post')),
            ],
        ),
        migrations.CreateModel(
            name='Panel',
            fields=[
                ('name', models.CharField(max_length=80, primary_key=True, serialize=False, verbose_name='Name')),
                ('lawyer_post', models.ManyToManyField(through='legitbase.LawyerPanel', to='legitbase.LawyerPost')),
            ],
        ),
        migrations.AddField(
            model_name='lawyerpanel',
            name='panel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='legitbase.Panel', verbose_name='Panel'),
        ),
    ]