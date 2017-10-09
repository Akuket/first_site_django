from django.contrib import admin

from payment.models import Product
from .models import Subscription


class ProductInLine(admin.TabularInline):
    model = Product
    max_num = 3
    readonly_fields = ('price', )



class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('description', {'fields': ['description']}),
    ]
    inlines = [ProductInLine]


admin.site.register(Subscription, SubscriptionAdmin)
