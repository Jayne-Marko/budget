import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Project, Category, Expense, RecurrentExpense
from django.views.generic import CreateView
from django.utils.text import slugify
from .forms import ExpenseForm, RecurrentExpenseForm


def project_list(request):
    project_list = Project.objects.all()
    return render(request, 'budget/project-list.html', {'project_list': project_list})


def project_detail(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    def get_daily_total():
        expense_list = Expense.objects.filter(project=project)
        expense_dates = [e.spend_date for e in expense_list]
        expense_dates.sort(reverse=True)
        day_expense_list = dict.fromkeys(expense_dates, 0)
        for expense in expense_list:
            day_expense_list.update({expense.spend_date: day_expense_list[expense.spend_date] + expense.amount})
        return day_expense_list

    if request.method == 'GET':
        category_list = Category.objects.filter(project=project)
        recurrent_expenses = RecurrentExpense.objects.filter(category='Регулярные')
        form_expense = ExpenseForm(request.POST)
        form_rec_expense = RecurrentExpense(request.POST)
        return render(request, 'budget/project-detail.html', {'project': project,
                                                              'expense_list': project.expenses.all(),
                                                              'day_expense_list': get_daily_total(),
                                                              'recurrent_expenses': recurrent_expenses,
                                                              'form_rec_expense': form_rec_expense,
                                                              'category_list': category_list, 'form_expense': form_expense})

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

            if category_name == 'Регулярные':
                RecurrentExpense.objects.create(
                    spend_date=spend_date,
                    comment=comment,
                    amount=amount,
                    category=category_name
                ).save()

        form_rec_expense = RecurrentExpenseForm(request.POST)
        if form_rec_expense.is_valid():
            spend_date = form_rec_expense.cleaned_data['spend_date']
            amount = form_rec_expense.cleaned_data['amount']
            category_name = form_rec_expense.cleaned_data['category']
            comment = form_rec_expense.cleaned_data['comment']

            # category = get_object_or_404(Category, project=project, name=category_name)

            RecurrentExpense.objects.create(
                spend_date=spend_date,
                comment=comment,
                amount=amount,
                category=category_name
            ).save()

    elif request.method == 'DELETE':
        id = json.loads(request.body)['id']
        expense = get_object_or_404(Expense, id=id)
        expense.delete()
        rec_expense = get_object_or_404(RecurrentExpense, id=id)
        rec_expense.delete()

        return HttpResponse('')

    return HttpResponseRedirect(project_slug)


def recurrent_expenses(request):
    recurrent_expenses = RecurrentExpense.objects.filter(category='Регулярные')

    if request.method == 'GET':
        form_rec_expense = RecurrentExpense(request.POST)
        return render(request, 'budget/recurrent-expenses.html', {'recurrent_expenses': recurrent_expenses,
                                                                  'form_rec_expense': form_rec_expense})

    elif request.method == 'POST':
        # process the form
        form_rec_expense = RecurrentExpenseForm(request.POST)
        if form_rec_expense.is_valid():
            spend_date = form_rec_expense.cleaned_data['spend_date']
            amount = form_rec_expense.cleaned_data['amount']
            category_name = form_rec_expense.cleaned_data['category']
            comment = form_rec_expense.cleaned_data['comment']

            RecurrentExpense.objects.create(
                spend_date=spend_date,
                comment=comment,
                amount=amount,
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
    fields = ('name', 'budget')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        categories = self.request.POST['categoriesString'].split(',')
        for category in categories:
            Category.objects.create(
                project=Project.objects.get(id=self.object.id),
                name=category
            ).save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return slugify(self.request.POST['name'])