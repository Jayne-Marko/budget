# Generated by Django 3.2.16 on 2023-01-01 22:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expense',
            options={'ordering': ('-amount',)},
        ),
        migrations.AddField(
            model_name='project',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 1, 1)),
        ),
        migrations.AddField(
            model_name='project',
            name='start_date',
            field=models.DateField(default=datetime.date(2023, 1, 1)),
        ),
        migrations.AlterField(
            model_name='expense',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='budget.project'),
        ),
    ]
