import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Project, Expense, RecurrentExpense
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from .forms import ExpenseForm, RecurrentExpenseForm
from django.urls import reverse_lazy


def project_list(request):
    project_list = Project.objects.all()
    return render(request, 'budget/project-list.html', {'project_list': project_list})


def add_recurrent(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    rec_expenses_list = RecurrentExpense.objects.all()
    current_rec_expense_list = Expense.objects.filter(project=project, category='Регулярные')
    cr_expense_comments = [e.comment for e in current_rec_expense_list]
    for rec_expense in rec_expenses_list:
        spend_date = datetime.today()
        if rec_expense.spend_date >= project.start_date.day:
            spend_date = datetime(year=project.start_date.year, month=project.start_date.month,
                                  day=rec_expense.spend_date)
        else:
            spend_date = datetime(year=project.end_date.year, month=project.end_date.month,
                                  day=rec_expense.spend_date)
        if rec_expense.comment not in cr_expense_comments:
            Expense.objects.create(
                project=project,
                spend_date=spend_date,
                comment=rec_expense.comment,
                amount=rec_expense.amount,
                category=rec_expense.category
            ).save()
    return render(request, "budget/add-recurrent.html", {'project': project})


def project_detail(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    def get_daily_total():
        expense_list = Expense.objects.filter(project=project)
        expense_dates = [e.spend_date for e in expense_list]
        expense_dates.sort(reverse=True)
        weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'cб', 'вс']
        day_expense_list = dict.fromkeys(expense_dates, ['', 0])
        for expense in expense_list:
            if expense.category != 'Доход':
                day_expense_list.update({expense.spend_date: [weekdays[expense.spend_date.weekday()], (day_expense_list[expense.spend_date][1] + expense.amount)]})
        return day_expense_list

    if request.method == 'GET':
        form_expense = ExpenseForm(request.POST)
        return render(request, 'budget/project-detail.html', {'project': project,
                                                              'expense_list': project.expenses.all(),
                                                              'day_expense_list': get_daily_total(),
                                                              'form_expense': form_expense})

    elif request.method == 'POST':
        # process the form
        form_expense = ExpenseForm(request.POST)
        if form_expense.is_valid():
            spend_date = form_expense.cleaned_data['spend_date']
            amount = form_expense.cleaned_data['amount']
            category_name = form_expense.cleaned_data['category']
            comment = form_expense.cleaned_data['comment']

            #category = get_object_or_404(Category, project=project, name=category_name)

            Expense.objects.create(
                project=project,
                spend_date=spend_date,
                comment=comment,
                amount=amount,
                category=category_name
            ).save()

    elif request.method == 'DELETE':
        id = json.loads(request.body)['id']
        expense = get_object_or_404(Expense, id=id)
        expense.delete()

        return HttpResponse('')

    return HttpResponseRedirect(project_slug)


def recurrent_expenses(request):
    recurrent_expenses = RecurrentExpense.objects.all()
    form_rec_expense = RecurrentExpenseForm(request.POST)
    if request.method == 'GET':
        return render(request, 'budget/recurrent-expenses.html', {'recurrent_expenses': recurrent_expenses,
                                                                  'form_rec_expense': form_rec_expense})

    elif request.method == 'POST':
        # process the form
        if form_rec_expense.is_valid():
            spend_date = form_rec_expense.cleaned_data['spend_date']
            amount = form_rec_expense.cleaned_data['amount']
            category_name = form_rec_expense.cleaned_data['category']
            comment = form_rec_expense.cleaned_data['comment']

            RecurrentExpense.objects.create(
                spend_date=spend_date,
                amount=amount,
                comment=comment,
                category=category_name
            ).save()

    elif request.method == 'DELETE':
        id = json.loads(request.body)['id']
        rec_expense = get_object_or_404(RecurrentExpense, id=id)
        rec_expense.delete()

        return HttpResponse('')

    return HttpResponseRedirect('recurrent')



class ProjectCreateView(CreateView):
    model = Project
    template_name = 'budget/add-project.html'
    fields = ('name', 'budget', 'start_date', 'end_date')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return slugify(self.request.POST['name'])


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'budget/edit-project.html'
    fields = ('name', 'budget', 'start_date', 'end_date')
    success_url = "/"


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'budget/delete-project.html'
    success_url = reverse_lazy('list')