from django.contrib import admin
from .models import Agent, Payment, Transaction, Good

# Customizing the admin interface for Agent model
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'current_balance')
    search_fields = ('name', 'email', 'phone')  # Enable search by name, email, or phone number
    list_filter = ('created_at',)  # Enable filtering by the creation date
    ordering = ('-created_at',)  # Default ordering by creation date (descending)

# Customizing the admin interface for Payment model
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'transaction', 'amount_paid', 'date_paid')  # Adjust these fields as necessary
    search_fields = ('agent')  # Search by agent name or transaction ID
    list_filter = ('date_paid',)  # Enable filtering by payment date
    ordering = ('-date_paid',)  # Default ordering by payment date (descending)

# Customizing the admin interface for Transaction model
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'good', 'quantity_disbursed', 'total_price', 'payment_status', 'due_date')
    search_fields = ('agent__name', 'good__name', 'payment_status')  # Enable search by agent, good, or status
    list_filter = ('payment_status', 'due_date')  # Enable filtering by payment status and due date
    ordering = ('-due_date',)  # Default ordering by due date (descending)

# Customizing the admin interface for Good model
class GoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_in_stock', 'price_per_g', 'created_at')
    search_fields = ('name',)  # Search by good name
    list_filter = ('created_at',)  # Enable filtering by the date the good was added
    ordering = ('-created_at',)  # Default ordering by date added (descending)

# Register your models with the admin site
admin.site.register(Agent, AgentAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Good, GoodAdmin)
