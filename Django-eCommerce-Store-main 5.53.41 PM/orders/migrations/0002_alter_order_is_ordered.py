# Generated by Django 4.2.7 on 2024-02-18 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='is_ordered',
            field=models.BooleanField(default=True),
        ),
    ]
