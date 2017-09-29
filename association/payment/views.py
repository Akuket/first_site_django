from django.http.response import Http404
from django.shortcuts import render

from . api_payplug import Payment
from . models import Subscription


def subscription_view(request):
    template_name = "payment/subscription.html"
    try:
        subscriptions = Subscription.objects.all()
    except Exception as e:
        raise e
    else:
        return render(request, template_name, {
            'subscriptions': subscriptions
        })


def payment_view(request, subscription, product):
    # ne fonctionne pas sur une adresse locale
    # return_url = request.build_absolute_uri(reverse("dashboard"))
    # cancel_url = request.build_absolute_uri(reverse("dashboard"))
    # hosted_payment = {'return_url': return_url, 'cancel_url': cancel_url}
    subscription_object = Subscription.objects.get(name=subscription)
    for products in subscription_object.products.all():
        if products.name == product:
            payment = Payment(request.user, product=products)
    return payment.redirect_payment() or Http404

