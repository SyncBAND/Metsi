from django.contrib import admin

from .models import Invoice, Payment, InvoiceCancelled, PaymentRefunded

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Invoice
admin.site.register(Invoice, InvoiceAdmin)

class InvoiceCancelledAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = InvoiceCancelled
admin.site.register(InvoiceCancelled, InvoiceCancelledAdmin)

class PaymentRefundedAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = PaymentRefunded
admin.site.register(PaymentRefunded, PaymentRefundedAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    class Meta:
        model = Payment
admin.site.register(Payment, PaymentAdmin)
