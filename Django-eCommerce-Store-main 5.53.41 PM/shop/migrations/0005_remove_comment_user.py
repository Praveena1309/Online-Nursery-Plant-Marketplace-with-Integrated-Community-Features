# Generated by Django 4.2.7 on 2024-02-23 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_comment_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
    ]