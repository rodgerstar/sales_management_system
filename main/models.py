from django.db import models
from datetime import timedelta, datetime
from django.db import transaction

from django.db.models import Sum

from django.utils import timezone

STATUS_CHOICES = [
    ('partial', 'Partial'),
    ('complete', 'Complete'),
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
]

class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    agent_number = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255)
    payment_period_days = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add balance field

    def __str__(self):
        return f"{self.agent_number} - {self.name}"

    class Meta:
        verbose_name_plural = "Agents"
        verbose_name = "Agent"
        ordering = ['agent_number']
        db_table = 'agents'


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
        # Set the thresholds for stock levels
        if self.quantity_in_stock > (self.quantity_in_stock / 2):
            return "In Stock"
        elif self.quantity_in_stock > (self.quantity_in_stock / 4):
            return "Almost Out"
        else:
            return "Out of Stock"

    class Meta:
        verbose_name_plural = "Goods"
        verbose_name = "Good"
        ordering = ['name']
        db_table = 'goods'




class Transaction(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='transactions')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='transactions')
    quantity_disbursed = models.FloatField()
    total_price = models.FloatField(editable=False)
    due_date = models.DateTimeField(editable=False)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='due')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity_disbursed * self.good.price_per_g

        # Set due date if not already set
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=self.agent.payment_period_days)

        # Ensure sufficient stock
        if self.good.quantity_in_stock < self.quantity_disbursed:
            raise ValueError("Insufficient stock to fulfill this transaction.")

        # Save the instance first to ensure it has a primary key
        if not self.pk:  # Save only if this is a new transaction
            super().save(*args, **kwargs)

        # Update payment status after calculating total paid
        total_paid = self.agent.payments.filter(transaction=self).aggregate(total=Sum('amount_paid'))['total'] or 0
        if total_paid >= self.total_price:
            self.payment_status = 'paid'
        else:
            # Use timezone.now() to get a timezone-aware current date
            current_date = timezone.now()

            # Ensure self.due_date is timezone-aware
            if timezone.is_naive(self.due_date):
                self.due_date = timezone.make_aware(self.due_date)

            # Perform the comparison of timezone-aware datetimes
            self.payment_status = 'late' if current_date > self.due_date else 'due'

        # Update stock and save transaction atomically
        with transaction.atomic():
            self.good.quantity_in_stock -= self.quantity_disbursed
            self.good.save()
            super().save(*args, **kwargs)  # Save again to update payment_status

    def __str__(self):
        return f"Transaction {self.id}: {self.agent.name} - {self.good.name} ({self.payment_status})"

    class Meta:
        verbose_name_plural = "Transactions"
        verbose_name = "Transaction"
        ordering = ['agent', 'good']
        db_table = 'transactions'

class Payment(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='payments')
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )  # Optional: Can associate payment with a specific transaction
    amount_paid = models.FloatField()
    date_paid = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save payment first
        super().save(*args, **kwargs)

        # Update transaction status if linked and payment is sufficient
        if self.transaction:
            total_paid = sum(payment.amount_paid for payment in self.transaction.payments.all())
            if total_paid >= self.transaction.total_price:
                self.transaction.payment_status = 'paid'
                self.transaction.save()

    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.agent.name} on {self.date_paid}"

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"
        ordering = ['-date_paid']
        db_table = 'payments'


