# Generated by Django 2.2.16 on 2022-01-29 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220104_1238'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date', '-pk']},
        ),
    ]
