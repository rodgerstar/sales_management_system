from django.db import models

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
    price = models.IntegerField()
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"

    class Meta:
        verbose_name_plural = "Goods"
        verbose_name = "Good"
        ordering = ['name']
        db_table = 'goods'


class Transaction(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='transactions')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='transactions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_distributed = models.DateTimeField(auto_now_add=True)
    expected_payment_date = models.DateTimeField()
    amount_due = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.id}: {self.agent.name} - {self.good.name}"

    class Meta:
        verbose_name_plural = "Transactions"
        verbose_name = "Transaction"
        ordering = ['agent', 'good']
        db_table = 'transactions'


class Payment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='partial')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id}: {self.amount_paid} - {self.transaction}"

    class Meta:
        verbose_name_plural = "Payments"
        verbose_name = "Payment"
        ordering = ['transaction', 'payment_date']
        db_table = 'payments'
