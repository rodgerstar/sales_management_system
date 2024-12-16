from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now

from main.app_forms import AgentForm, GoodsForm, TransactionForm

from .models import Agent, Transaction, Payment, Good

# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html')


def process_payment(request):
    agents = Agent.objects.all()
    transactions = Transaction.objects.filter(payment_status__in=['due', 'late'])

    if request.method == 'POST':
        agent_id = request.POST.get('agent')
        transaction_id = request.POST.get('transaction', None)
        amount_paid = float(request.POST.get('amount_paid'))

        try:
            agent = Agent.objects.get(id=agent_id)
            transaction = Transaction.objects.get(id=transaction_id) if transaction_id else None

            # Record payment
            payment = Payment(agent=agent, transaction=transaction, amount_paid=amount_paid)
            payment.save()

            return render(request, 'agents.html')
        except Agent.DoesNotExist:
            return HttpResponse("Error: Agent not found.")
        except Transaction.DoesNotExist:
            return HttpResponse("Error: Transaction not found.")
        except ValueError as e:
            return HttpResponse(f"Error: {e}")

    return render(request, 'payment_form.html', {'agents': agents, 'transactions': transactions})

def calculate_agent_balance(agent_id):
    agent = Agent.objects.get(id=agent_id)
    total_due = sum(
        t.total_price for t in agent.transactions.filter(payment_status__in=['due', 'late'])
    )
    total_paid = sum(
        p.amount_paid for p in agent.payments.all()
    )
    return total_due - total_paid


def agent_details(request, agent_id):
    agent = Agent.objects.get(id=agent_id)
    transactions = agent.transactions.all()
    payments = agent.payments.all()
    balance = calculate_agent_balance(agent_id)

    return render(request, 'agent_details.html', {
        'agent': agent,
        'transactions': transactions,
        'payments': payments,
        'balance': balance,
    })


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest

def distributed_goods(request):
    agents = Agent.objects.all()
    goods = Good.objects.filter(quantity_in_stock__gt=0)

    if request.method == "POST":
        agent_id = request.POST.get('agent')
        good_id = request.POST.get('good')
        quantity_disbursed = request.POST.get('quantity_disbursed')

        if not agent_id or not good_id or not quantity_disbursed:
            return HttpResponseBadRequest("Missing required fields.")

        try:
            quantity_disbursed = float(quantity_disbursed)
            agent = get_object_or_404(Agent, pk=agent_id)
            good = get_object_or_404(Good, pk=good_id)

            if good.quantity_in_stock < quantity_disbursed:
                return render(request, 'transaction_form.html', {
                    'agents': agents,
                    'goods': goods,
                    'error': "Insufficient stock for the selected good.",
                })

            # Create the transaction
            transaction = Transaction.objects.create(
                agent=agent,
                good=good,
                quantity_disbursed=quantity_disbursed,
            )

            return render(request, 'agents.html', {
                'message': 'Transaction recorded successfully!',
                'transaction': transaction
            })
        except ValueError as e:
            return HttpResponseBadRequest(f"Invalid input: {e}")

    return render(request, 'transaction_form.html', {
        'agents': agents,
        'goods': goods,
    })
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