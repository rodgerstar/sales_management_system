from django.contrib import messages
from django.shortcuts import  redirect, get_object_or_404
from django.utils import timezone
from main.app_forms import AgentForm, GoodsForm
from .models import  Payment, Good
from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Agent, Transaction
from django.db.models import Q

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

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

            # Update transaction's payment status
            if transaction:
                total_paid = transaction.payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0.0
                if total_paid >= transaction.total_price:
                    transaction.payment_status = 'paid'
                else:
                    current_date = timezone.now()
                    transaction.payment_status = 'late' if current_date > transaction.due_date else 'due'
                transaction.save()

            # Update agent balance
            agent.update_agent_balance()

            messages.success(request, "Payment processed successfully!")
            return redirect('agent_details', agent_id=agent.id)

        except (Agent.DoesNotExist, Transaction.DoesNotExist):
            messages.error(request, "Agent or Transaction not found.")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, 'payment_form.html', {'agents': agents, 'transactions': transactions})

def agent_details(request, agent_id):
    try:
        agent = Agent.objects.get(id=agent_id)
        transactions = Transaction.objects.filter(agent=agent)
        payments = Payment.objects.filter(agent=agent)

        # Get the balance using the model's current_balance property
        balance = agent.current_balance

        context = {
            'agent': agent,
            'transactions': transactions,
            'payments': payments,
            'balance': balance,
        }

        return render(request, 'agent_details.html', context)

    except Agent.DoesNotExist:
        messages.error(request, "Agent not found.")
        return redirect('agents')

def distributed_goods(request):
    agents = Agent.objects.all()
    goods = Good.objects.filter(quantity_in_stock__gt=0)

    if request.method == "POST":
        agent_id = request.POST.get('agent')
        good_id = request.POST.get('good')
        quantity_disbursed = request.POST.get('quantity_disbursed')

        if not agent_id or not good_id or not quantity_disbursed:
            messages.error(request, "All fields are required.")
            return render(request, 'transaction_form.html', {'agents': agents, 'goods': goods})

        try:
            quantity_disbursed = float(quantity_disbursed)
            agent = get_object_or_404(Agent, pk=agent_id)
            good = get_object_or_404(Good, pk=good_id)

            if quantity_disbursed > good.quantity_in_stock:
                messages.error(request, "Insufficient stock for the selected good.")
                return render(request, 'transaction_form.html', {'agents': agents, 'goods': goods})

            # Create a new transaction
            transaction = Transaction.objects.create(
                agent=agent,
                good=good,
                quantity_disbursed=quantity_disbursed,
                payment_status='due',
            )

            # Update stock
            good.quantity_in_stock -= quantity_disbursed
            good.save()

            messages.success(request, "Transaction recorded successfully!")
            return redirect('agent_details', agent_id=agent.id)

        except ValueError:
            messages.error(request, "Invalid quantity entered.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, 'transaction_form.html', {'agents': agents, 'goods': goods})

def outstanding_balances(request):
    # Annotate agents with outstanding balances and transactions
    agents = Agent.objects.annotate(
        total_outstanding=Sum(
            ExpressionWrapper(
                F('transactions__total_price') - F('transactions__payments__amount_paid'),
                output_field=DecimalField()
            ),
            filter=~Q(transactions__payment_status='paid')
        )
    ).filter(total_outstanding__gt=0)

    # Fetch outstanding transactions grouped by goods
    outstanding_goods = Transaction.objects.filter(payment_status__in=['due', 'late']).values(
        'good__name', 'agent__name'
    ).annotate(
        total_quantity=Sum('quantity_disbursed'),
        total_balance=Sum(
            ExpressionWrapper(
                F('total_price') - F('payments__amount_paid'),
                output_field=DecimalField()
            )
        )
    )

    context = {
        'agents': agents,
        'outstanding_goods': outstanding_goods,
    }
    return render(request, 'outstanding.html', context)


def agent_reports(request):
    # Add functionality for agent reports here (e.g., filtering by date range, agent type, etc.)
    reports = Agent.objects.all()  # Placeholder for actual report generation
    return render(request, 'agent_reports.html', {'reports': reports})

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

def pie_chart(request):
    return None

def line_chart(request):
    return None

def bar_chart(request):
    return None

