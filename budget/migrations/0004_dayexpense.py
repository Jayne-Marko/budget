# Generated by Django 3.2.16 on 2023-01-02 17:38

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0003_alter_expense_spend_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spend_date', models.DateField(default=datetime.date(2023, 1, 2))),
                ('total_amount', models.IntegerField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_expenses', to='budget.project')),
            ],
        ),
    ]