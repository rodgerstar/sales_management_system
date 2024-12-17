from datetime import timedelta, datetime

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from django.utils import timezone
from datetime import datetime
from django.db import transaction as db_transaction  # For atomic transactions
from main.app_forms import AgentForm, GoodsForm, TransactionForm
from .models import Agent, Transaction, Payment, Good


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
            # Validate agent and transaction
            agent = Agent.objects.get(id=agent_id)
            transaction = Transaction.objects.get(id=transaction_id) if transaction_id else None

            # Record the payment
            payment = Payment(agent=agent, transaction=transaction, amount_paid=amount_paid)
            payment.save()

            # Update the transaction's payment status
            if transaction:
                total_paid = transaction.payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0.0
                if total_paid >= transaction.total_price:
                    transaction.payment_status = 'paid'
                else:
                    # Use timezone-aware comparison
                    current_date = timezone.now()
                    due_date = timezone.make_aware(transaction.due_date) if timezone.is_naive(
                        transaction.due_date) else transaction.due_date
                    transaction.payment_status = 'late' if current_date > due_date else 'due'

                transaction.save()

            # No stock adjustments here!

            messages.success(request, "Payment processed successfully!")
            return redirect('agent_details', agent_id=agent.id)
        except (Agent.DoesNotExist, Transaction.DoesNotExist):
            messages.error(request, "Agent or Transaction not found.")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, 'payment_form.html', {'agents': agents, 'transactions': transactions})


def calculate_agent_balance(agent_id):
    agent = Agent.objects.get(id=agent_id)

    # Calculate total due (for transactions that are 'due' or 'late')
    total_due = sum(
        t.total_price for t in agent.transactions.filter(payment_status__in=['due', 'late'])
    )

    # Calculate total paid (for all payments associated with the agent)
    total_paid = sum(
        p.amount_paid for p in agent.payments.all()
    )

    # Return the balance (difference between total due and total paid)
    return total_due - total_paid


def agent_details(request, agent_id):
    agent = Agent.objects.get(id=agent_id)
    transactions = Transaction.objects.filter(agent=agent)
    payments = Payment.objects.filter(agent=agent)

    # Aggregate the total due and total paid, using 0.0 as the default if None
    total_due = transactions.aggregate(total_due=Sum('total_price'))['total_due'] or 0.0
    total_paid = payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0.0

    # Calculate the balance
    balance = total_due - total_paid

    context = {
        'agent': agent,
        'transactions': transactions,
        'payments': payments,
        'balance': balance,
    }

    return render(request, 'agent_details.html', context)


def distributed_goods(request):
    # Fetch all agents and goods
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

            # Use atomic transactions to ensure data consistency
            with db_transaction.atomic():
                # Create a new transaction
                transaction = Transaction.objects.create(
                    agent=agent,
                    good=good,
                    quantity_disbursed=quantity_disbursed,
                    payment_status='due',  # Default status
                )

                # Log successful transaction creation
                messages.success(request, "Transaction recorded successfully!")

                # Redirect to agents page or wherever you'd like
                return redirect('agents')

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            # Log unexpected errors
            messages.error(request, f"An error occurred: {str(e)}")
            print(f"DEBUG: {e}")  # Optional: For debugging during development

    # Render the form for GET request
    return render(request, 'transaction_form.html', {'agents': agents, 'goods': goods})

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

    @property
    def outstanding_balance(self):
        total_due = self.transactions.aggregate(total_due=Sum('total_price'))['total_due'] or 0
        total_paid = self.payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
        return total_due - total_paid

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
