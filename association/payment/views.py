import payplug
import datetime
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from . api_payplug import Payment
from . models import Subscription, Product
from account.api import accreditation_view_required
from account.models import PaymentsUser


@accreditation_view_required(redirect_url=reverse_lazy(u'login')) # si authentifié et email valide
def subscription_view(request):
    template_name = "payment/subscription.html"
    subscriptions = Subscription.objects.all()
    return render(request, template_name, {
        'subscriptions': subscriptions
    })


@accreditation_view_required(redirect_url=reverse_lazy(u'login'))  # si authentifié et email valide
def payment_view(request, subscription, product):
    # ne fonctionne pas sur une adresse locale
    return_url = request.build_absolute_uri(reverse("notifications payplug"))
    cancel_url = request.build_absolute_uri(reverse("subscriptions"))
    # ne fonctionne pas chez moi, surment du au firewall de pythonanywhere
    # notification_url = request.build_absolute_uri(reverse("notifications payplug"))
    hosted_payment = {'return_url': return_url, 'cancel_url': cancel_url}
    subscription_object = Subscription.objects.get(name=subscription)
    for products in subscription_object.products.all():
        if products.name == product:
            payment = Payment(request.user, subscription=subscription_object, product=products,
                              payment_infos={'hosted_payment': hosted_payment})
            return payment.redirect_payment()
    return HttpResponseNotFound('<h1>Http 404</h1>')


def notifications_payplug_view(request):
    # template_name = "payment/notifications.html"
    date = datetime.date.today()
    try:
        payment_id = PaymentsUser.objects.filter(user=request.user).order_by("-date")[0]
        payment = payplug.Payment.retrieve(payment_id.reference)
        product = Product.objects.get(name=payment_id.product.name, subscription=payment_id.subscription)
    except payplug.exceptions.PayplugError as e:
        raise e
    else:
        if payment.failure is not None:
            return HttpResponseRedirect(reverse(u'payment_error', args={
                "payment_id": payment_id
            }))
        if payment.is_paid == True:
            request.user.accreditation = 2
            request.user.subscription = payment_id.subscription.name
            request.user.product = product.name
            request.user.subscriber = date + datetime.timedelta(product.duration)
            request.user.save()
            return HttpResponseRedirect(reverse_lazy(u'dashboard'))
    return HttpResponseRedirect(reverse_lazy(u'payment'))


def error_view(request, payment_id):
    payment = payplug.Payment.retrieve(payment_id.reference)
    code_error, message_error = payment.failure.code, payment.failure.message
    if code_error == 'card_declined' or 'processing_error' or \
            'insufficient_funds' or 'incorrect_number':
        return HttpResponseRedirect(payment.hosted_payment.payment_url)
    elif code_error == 'aborted' or 'timeout':
        return HttpResponseRedirect(reverse_lazy(u'payment'))
    elif code_error == 'fraud_suspected':
        return HttpResponseRedirect(reverse_lazy(u'logout'))



