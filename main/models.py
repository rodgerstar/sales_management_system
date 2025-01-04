from django.db import models
from datetime import timedelta
from django.db import transaction as db_transaction
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ValidationError

class Agent(models.Model):
    AGENT_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('commission', 'Commission'),
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    agent_number = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255)
    payment_period_days = models.IntegerField(default=30)
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES, default='regular')
    commission_rate = models.FloatField(null=True, blank=True, help_text="Commission rate per 1000 sold")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def clean(self):
        if self.agent_type == 'commission' and self.commission_rate is None:
            raise ValidationError("Commission rate is required for commission-based agents.")

    def __str__(self):
        return f"{self.agent_number} - {self.name}"

    class Meta:
        verbose_name_plural = "Agents"
        verbose_name = "Agent"
        ordering = ['agent_number']
        db_table = 'agents'

    @property
    def current_balance(self):
        """Calculates and returns the current balance the agent owes to the business."""

        total_paid = self.payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0.0
        total_disbursed = self.transactions.aggregate(total_disbursed=Sum('total_price'))['total_disbursed'] or 0.0

        if self.agent_type == 'commission' and self.commission_rate:
            commission = (total_disbursed / 1000) * self.commission_rate
            return total_disbursed - commission - total_paid
        return total_disbursed - total_paid



class Good(models.Model):
    name = models.CharField(max_length=100)
    price_per_g = models.FloatField()
    quantity_in_stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.quantity_in_stock}kg @ {self.price_per_g}/g"

    @property
    def stock_status(self):
        if self.quantity_in_stock > 50:
            return "In Stock"
        elif self.quantity_in_stock > 10:
            return "Almost Out"
        else:
            return "Out of Stock"

    class Meta:
        verbose_name_plural = "Goods"
        verbose_name = "Good"
        ordering = ['name']
        db_table = 'goods'


class Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('late', 'Late'),
    )

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='transactions')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='transactions')
    quantity_disbursed = models.FloatField()
    total_price = models.FloatField(editable=False)
    due_date = models.DateTimeField(editable=False)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='due')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity_disbursed * self.good.price_per_g
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=self.agent.payment_period_days)

        with db_transaction.atomic():
            if not self.pk:
                if self.good.quantity_in_stock < self.quantity_disbursed:
                    raise ValueError("Insufficient stock to fulfill this transaction.")
                self.good.quantity_in_stock -= self.quantity_disbursed
                self.good.save()

            super().save(*args, **kwargs)

        total_paid = self.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
        if total_paid >= self.total_price:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'late' if timezone.now() > self.due_date else 'due'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.id}: {self.agent.name} - {self.good.name} ({self.payment_status})"

    class Meta:
        verbose_name_plural = "Transactions"
        verbose_name = "Transaction"
        ordering = ['agent', 'good']
        db_table = 'transactions'


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('late', 'Late'),
    )

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='payments')
    transaction = models.ForeignKey(
        'Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount_paid = models.FloatField()
    date_paid = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.transaction:
            total_paid = self.transaction.payments.aggregate(total=Sum('amount_paid'))['total'] or 0
            if total_paid >= self.transaction.total_price:
                self.transaction.payment_status = 'paid'
            else:
                self.transaction.payment_status = 'due'
            self.transaction.save()

        self.update_agent_balance()

    def update_agent_balance(self):
        """Update agent balance after payment and transaction status changes."""
        agent = self.agent

        total_paid = agent.payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0.0
        total_disbursed = agent.transactions.aggregate(total_disbursed=Sum('total_price'))['total_disbursed'] or 0.0

        commission = 0.0
        if agent.agent_type == 'commission' and agent.commission_rate:
            commission = (total_disbursed / 1000) * agent.commission_rate

        new_balance = total_disbursed - commission - total_paid
        agent.balance = new_balance
        agent.save()

    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.agent.name} on {self.date_paid}"

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"
        ordering = ['-date_paid']
        db_table = 'payments'