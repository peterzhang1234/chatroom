# Generated by Django 2.2.1 on 2020-06-21 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='email',
        ),
    ]
