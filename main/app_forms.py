from django import forms

from main.models import Agent, Good, Transaction


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'phone', 'agent_number', 'email', 'address', 'payment_period_days']

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name', 'price_per_g', 'quantity_in_stock']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['agent', 'good', 'quantity_disbursed']