# Generated by Django 2.0.5 on 2018-05-29 08:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rest_im', '0005_auto_20180529_1536'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Friends',
            new_name='Friend',
        ),
        migrations.AddField(
            model_name='message',
            name='msg_create',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='message',
            name='msg_content',
            field=models.TextField(max_length=1000),
        ),
    ]
