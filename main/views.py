from django.shortcuts import render, redirect

from main.app_forms import AgentForm, GoodsForm, TransactionForm
from main.models import Agent, Good


# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html')


def distributed_goods(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agent')
    else:
        form = GoodsForm()
    return render(request, 'transaction_form.html', {'form': form})


def payments(request):
    return None


def agent_balances(request):
    return None


def agent_reports(request):
    return None


def add_goods(request):
    if request.method == "POST":
        form = GoodsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('goods')
    else:
        form = GoodsForm()
    return render(request, 'goods_form.html', {'form': form})


def agent(request):
    data = Agent.objects.all()
    return render(request, 'agents.html', {'data': data})


def add_agent(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agent')
    else:
        form = AgentForm()
    return render(request, 'agents_form.html', {'form': form})


def general_reports(request):
    return None


def goods(request):
   data = Good.objects.all()
   return render(request, 'goods.html', {'data': data})