from django.contrib import admin

from payment.models import Product
from .models import Subscription


class ProductInLine(admin.TabularInline):
    model = Product
    max_num = 3


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'informations')
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('informations', {'fields': ['informations']}),
    ]
    inlines = [ProductInLine]


admin.site.register(Subscription, SubscriptionAdmin)
