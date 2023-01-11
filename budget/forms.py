from django import forms
from django.forms import NumberInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

spends = [
    ('Daily', 'Daily'),
    ('Plan', 'Plan'),
    ('Recurr', 'Recurr'),
    ('Income', 'Income')
]

recurrent = [
    ('Recurr', 'Recurr')
]


class ExpenseForm(forms.Form):
    spend_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label='Дата')
    amount = forms.CharField(label='Сумма')
    category = forms.ChoiceField(choices=spends, label='Категория')
    comment = forms.CharField(required=False, label='Комментарий')


class RecurrentExpenseForm(forms.Form):
    spend_date = forms.IntegerField(label='Число (день месяца)')
    amount = forms.IntegerField(label='Сумма')
    category = forms.ChoiceField(choices=recurrent, label='Категория')
    comment = forms.CharField(required=False, label='Комментарий')


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    #first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    #last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'