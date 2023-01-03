from django.contrib import admin
from .models import Project, Expense, RecurrentExpense
# Register your models here.

admin.site.register(Project)
admin.site.register(Expense)
admin.site.register(RecurrentExpense)