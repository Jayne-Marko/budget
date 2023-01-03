from django import forms
from django.forms import NumberInput

spends = [
    ('Повседневные', 'Повседневные'),
    ('Запланированные', 'Запланированные'),
    ('Регулярные', 'Регулярные'),
]

recurrent = [
    ('Регулярные', 'Регулярные')
]

class ExpenseForm(forms.Form):
    spend_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    amount = forms.IntegerField()
    category = forms.ChoiceField(choices=spends)
    comment = forms.CharField(required=False)


class RecurrentExpenseForm(forms.Form):
    spend_date = forms.IntegerField()
    amount = forms.IntegerField()
    category = forms.ChoiceField(choices=recurrent)
    comment = forms.CharField(required=False)