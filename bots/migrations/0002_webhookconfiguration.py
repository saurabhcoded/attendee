# Generated by Django 5.1.2 on 2024-12-15 03:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(editable=False, max_length=32, unique=True)),
                ('webhook_type', models.IntegerField(choices=[(1, 'Bot State Change'), (2, 'Recording or Transcription State Change')])),
                ('destination_url', models.URLField(max_length=2048)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhook_configurations', to='bots.project')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('project', 'webhook_type', 'destination_url'), name='unique_webhook_configuration')],
            },
        ),
    ]
