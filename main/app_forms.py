from django import forms

from main.models import Agent, Good


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'phone', 'agent_number', 'email', 'address']

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name', 'price', 'quantity']
