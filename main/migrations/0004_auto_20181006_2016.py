# Generated by Django 2.0.7 on 2018-10-06 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20181001_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addstage',
            name='run',
        ),
        migrations.AlterField(
            model_name='stage',
            name='state',
            field=models.CharField(choices=[('STD', 'Not Ready'), ('RDY', 'Ready to Start'), ('GO', 'Running'), ('FIN', 'Finished'), ('LCK', 'Finished and Confirmed')], default='STD', max_length=3),
        ),
    ]