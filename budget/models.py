from datetime import date
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Project(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    budget = models.IntegerField(default=57025)
    start_date = models.DateField(default=date.today())
    end_date = models.DateField(default=date.today())

    def save(self, *args, **kwargs):
        month_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь','Октябрь', 'Ноябрь', 'Декабрь']
        self.name = month_name[self.start_date.month - 1] + " " + str(self.start_date.year)
        self.slug = slugify(str(self.start_date))
        super(Project, self).save(*args, **kwargs)

    def budget_left(self):
        expense_list = Expense.objects.filter(project=self)
        total_expense_amount = 0
        total_income = self.budget
        for expense in expense_list:
            if expense.category != 'Income' and expense.spend_date <= date.today():
                total_expense_amount += expense.amount
            elif expense.category == 'Income':
                total_income += expense.amount
        return total_income - total_expense_amount

    def days_to_income(self):
        if self.start_date <= date.today() <= self.end_date:
            return (self.end_date - date.today()).days
        else:
            return (self.end_date - self.start_date).days

    def daily_budget(self):
        days_left = self.days_to_income()
        budget_left = self.budget_left()
        try:
            return round(budget_left / days_left)
        except:
            return 0

    def current_month(self):
        if self.start_date <= date.today() <= self.end_date:
            return True

    class Meta:
        ordering = ('-start_date', )


class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    spend_date = models.DateField(default=date.today())
    comment = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100)

    def week_day(self):
        weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'cб', 'вс']
        return weekdays[self.spend_date.weekday()]

    class Meta:
        ordering = ('-spend_date', )


class RecurrentExpense(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    spend_date = models.IntegerField()
    comment = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100)

    def get_category(self):
        self.category = 'Recurr'
        self.save()

    class Meta:
        ordering = ('spend_date', )
