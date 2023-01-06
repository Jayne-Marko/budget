from datetime import date, timedelta
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    budget = models.IntegerField(default=57025)
    start_date = models.DateField(default=date.today())
    end_date = models.DateField(default=date.today())

    def get_default_start_date(self):
        month_list = Project.objects.all()
        max_start_date = [month.start_date for month in month_list]
        return max(max_start_date)

    def save(self, *args, **kwargs):
        month_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь','Октябрь', 'Ноябрь', 'Декабрь']
        month_slug = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        self.name = month_name[self.start_date.month - 1]
        self.slug = slugify(month_slug[self.start_date.month - 1])
        super(Project, self).save(*args, **kwargs)

    def budget_left(self):
        expense_list = Expense.objects.filter(project=self)
        total_expense_amount = 0
        total_income = self.budget
        for expense in expense_list:
            if expense.category != 'Доход':
                total_expense_amount += expense.amount
            else:
                total_income += expense.amount
        return total_income - total_expense_amount

    def days_to_income(self):
        if date.today() < self.start_date:
            return (self.end_date - self.start_date).days
        else:
            return (self.end_date - date.today()).days

    def daily_budget(self):
        days_left = self.days_to_income()
        budget_left = self.budget_left()
        try:
            return round(budget_left / days_left)
        except:
            return 0


class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    spend_date = models.DateField(default=date.today())
    comment = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField()
    category = models.CharField(max_length=100)

    def week_day(self):
        weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'cб', 'вс']
        return weekdays[self.spend_date.weekday()]

    class Meta:
        ordering = ('-spend_date', )


class RecurrentExpense(models.Model):
    spend_date = models.IntegerField()
    comment = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField()
    category = models.CharField(max_length=100)

    def get_category(self):
        self.category = 'Регулярные'
        self.save()

    class Meta:
        ordering = ('-spend_date', )