# Generated by Django 4.1.2 on 2023-09-03 03:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_submission_max_score_submission_passed_ratio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='submission_output',
            field=models.CharField(default='-', max_length=100000),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='SubmissionOutput',
            fields=[
                ('submission_output_id', models.AutoField(primary_key=True, serialize=False)),
                ('output', models.CharField(max_length=100000)),
                ('runtime_status', models.CharField(max_length=10)),
                ('submission', models.ForeignKey(db_column='submission_id', on_delete=django.db.models.deletion.CASCADE, to='api.submission')),
            ],
        ),
    ]
