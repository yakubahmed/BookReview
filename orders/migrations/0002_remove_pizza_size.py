# Generated by Django 2.2.5 on 2019-09-17 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pizza',
            name='size',
        ),
    ]
