from django.db import models
from datetime import timedelta, datetime

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

        # Set due date based on the agent's payment period
        if not self.due_date:
            self.due_date = datetime.now() + timedelta(days=self.agent.payment_period_days)

        # Determine payment status
        current_date = datetime.now()
        if self.payment_status != 'paid':  # Only update if payment hasn't been marked as 'paid'
            if current_date > self.due_date:
                self.payment_status = 'late'
            else:
                self.payment_status = 'due'

        # Update stock
        if self.good.quantity_in_stock >= self.quantity_disbursed:
            self.good.quantity_in_stock -= self.quantity_disbursed
            self.good.save()
        else:
            raise ValueError("Insufficient stock to fulfill this transaction.")

        super().save(*args, **kwargs)

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
        # Update transaction status if linked and payment is sufficient
        if self.transaction:
            total_paid = sum(payment.amount_paid for payment in self.transaction.payments.all())
            if total_paid >= self.transaction.total_price:
                self.transaction.payment_status = 'paid'
                self.transaction.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.agent.name} on {self.date_paid}"

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"
        ordering = ['-date_paid']
        db_table = 'payments'


