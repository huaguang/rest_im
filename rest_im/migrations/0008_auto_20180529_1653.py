# Generated by Django 2.0.5 on 2018-05-29 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_im', '0007_auto_20180529_1643'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('msg_create',)},
        ),
    ]
