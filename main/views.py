from django.shortcuts import render

from main.app_forms import AgentForm, GoodsForm


# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html')


def distributed_goods(request):
    return None


def payments(request):
    return None


def agent_balances(request):
    return None


def agent_reports(request):
    return None


def add_goods(request):
    form = GoodsForm()
    return render(request, 'goods_form.html', {'form': form})


def agent(request):
    return None


def add_agent(request):
    form = AgentForm()
    return render(request, 'agents_form.html', {'form': form})


def general_reports(request):
    return None