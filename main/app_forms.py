from django import forms
from django.contrib.auth.forms import UserCreationForm
from main.models import Agent, Good, Transaction
from django.contrib.auth.models import User


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'phone', 'agent_number', 'email', 'address', 'payment_period_days', 'agent_type', 'commission_rate']

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name', 'price_per_g', 'quantity_in_stock']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['agent', 'good', 'quantity_disbursed']

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']