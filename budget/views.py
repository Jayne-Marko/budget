import json
import calendar
from datetime import datetime, date
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Project, Expense, RecurrentExpense
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from .forms import ExpenseForm, RecurrentExpenseForm, RegisterUserForm
from django.urls import reverse_lazy
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home(request):
    return render(request, 'budget/home.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list')
        else:
            messages.success(request, ("Неправильный логин или пароль"))
            return redirect('login')

    else:
        return render(request, 'registration/login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You Were Logged Out!"))
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('list')
    else:
        form = RegisterUserForm()

    return render(request, 'registration/register.html', {'form': form,})


@login_required
def project_list(request):
    project_list = Project.objects.filter(user_id=request.user)
    past_months = [month for month in project_list if month.start_date <= date.today()]
    fututre_months = [month for month in project_list if month.start_date > date.today()]
    currency = ['₽', 'Kč', '€', '$']
    return render(request, 'budget/project-list.html', {'past_months': past_months,
                                                        'future_months': fututre_months,
                                                        'project_list': project_list,
                                                        'currency': currency
                                                        })


@login_required
def add_recurrent(request, project_slug):
    project = get_object_or_404(Project, user_id=request.user, slug=project_slug)
    rec_expenses_list = RecurrentExpense.objects.filter(user_id=request.user)
    current_rec_expense_list = Expense.objects.filter(project=project, category='Recurr')
    cr_expense_comments = [e.comment for e in current_rec_expense_list]
    for rec_expense in rec_expenses_list:
        if rec_expense.spend_date >= project.start_date.day:
            try:
                spend_date = datetime(year=project.start_date.year, month=project.start_date.month,
                                      day=rec_expense.spend_date)
            except:
                last_day = calendar.monthrange(project.start_date.year, project.start_date.month)
                spend_date = datetime(year=project.start_date.year, month=project.start_date.month,
                                      day=last_day[1])
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
    return redirect('detail', project_slug=project.slug)


@login_required
def project_detail(request, project_slug):
    project = get_object_or_404(Project, user_id=request.user, slug=project_slug)

    def get_daily_total():
        expense_list = Expense.objects.filter(project=project)
        expense_dates = [e.spend_date for e in expense_list]
        expense_dates.sort(reverse=True)
        weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'cб', 'вс']
        day_expense_list = dict.fromkeys(expense_dates, ['', 0])
        for expense in expense_list:
            if expense.category != 'Income':
                day_expense_list.update({expense.spend_date: [weekdays[expense.spend_date.weekday()], (
                        day_expense_list[expense.spend_date][1] + expense.amount)]})
        return day_expense_list

    if request.method == 'GET':
        form_expense = ExpenseForm(request.POST)
        return render(request, 'budget/project-detail.html', {'project': project,
                                                              'expense_list': project.expenses.all(),
                                                              'day_expense_list': get_daily_total(),
                                                              'form_expense': form_expense,
                                                              })

    elif request.method == 'POST':
        # process the form
        form_expense = ExpenseForm(request.POST)
        if form_expense.is_valid():
            spend_date = form_expense.cleaned_data['spend_date']
            amount = form_expense.cleaned_data['amount']
            category_name = form_expense.cleaned_data['category']
            comment = form_expense.cleaned_data['comment']

            # category = get_object_or_404(Category, project=project, name=category_name)
            sum_amount = eval(amount)

            Expense.objects.create(
                project=project,
                spend_date=spend_date,
                comment=comment,
                amount=sum_amount,
                category=category_name
            ).save()

    elif request.method == 'DELETE':
        id = json.loads(request.body)['id']
        expense = get_object_or_404(Expense, id=id)
        expense.delete()

        return HttpResponse('')

    return HttpResponseRedirect(project_slug)


@login_required
def recurrent_expenses(request):
    recurrent_expenses = RecurrentExpense.objects.filter(user_id=request.user)
    form_rec_expense = RecurrentExpenseForm(request.POST)
    if request.method == 'GET':
        return render(request, 'budget/recurrent-expenses.html', {'recurrent_expenses': recurrent_expenses,
                                                                  'form_rec_expense': form_rec_expense
                                                                  })

    elif request.method == 'POST':
        # process the form
        if form_rec_expense.is_valid():
            spend_date = form_rec_expense.cleaned_data['spend_date']
            amount = form_rec_expense.cleaned_data['amount']
            category_name = form_rec_expense.cleaned_data['category']
            comment = form_rec_expense.cleaned_data['comment']

            RecurrentExpense.objects.create(
                user_id=request.user,
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
    fields = ['budget', 'start_date', 'end_date']

    def get_form(self, form_class=None):
        form = super(ProjectCreateView, self).get_form(form_class)
        form.instance.user_id = self.request.user
        form.fields['start_date'].widget = AdminDateWidget(attrs={'type': 'date'})
        form.fields['end_date'].widget = AdminDateWidget(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        return HttpResponseRedirect('list')


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'budget/edit-project.html'
    fields = ('name', 'budget', 'start_date', 'end_date')
    success_url = reverse_lazy('list')


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'budget/delete-project.html'
    success_url = reverse_lazy('list')



