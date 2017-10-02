from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from . api_payplug import Payment
from . models import Subscription
from account.api import accreditation_view_required


@accreditation_view_required(redirect_url=reverse_lazy(u'login')) # si authentifié et email valide
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

@accreditation_view_required(redirect_url=reverse_lazy(u'login')) # si authentifié et email valide
def payment_view(request, subscription, product):
    # ne fonctionne pas sur une adresse locale
    return_url = request.build_absolute_uri(reverse("dashboard"))
    cancel_url = request.build_absolute_uri(reverse("subscriptions"))
    hosted_payment = {'return_url': return_url, 'cancel_url': cancel_url}
    subscription_object = Subscription.objects.get(name=subscription)
    for products in subscription_object.products.all():
        if products.name == product:
            payment = Payment(request.user, product=products, payment_infos={'hosted_payment': hosted_payment})
            return payment.redirect_payment()
    return HttpResponseNotFound('<h1>Http 404</h1>')
