# Generated by Django 4.1.2 on 2023-12-12 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_rename_depricated_testcase_deprecated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='output',
            field=models.CharField(max_length=100000, null=True),
        ),
    ]
