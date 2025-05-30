# Generated by Django 4.2.21 on 2025-05-15 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('manager', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_manager', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
