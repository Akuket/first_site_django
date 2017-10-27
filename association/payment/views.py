import payplug
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from payment.models import Product
from .api_payplug import create_classic_payment, update_payment
from .models import Subscription
from account.api import accreditation_view_required


@accreditation_view_required(redirect_url=reverse_lazy(u'login'))  # If connected and and has a confirmed email address
def subscription_view(request):
    """
    A view of all subscriptions available

    :param request: Request object
    :return: Render of the view
    """
    template_name = "payment/subscription.html"
    subscriptions = Subscription.objects.all()
    return render(request, template_name, {
        'subscriptions': subscriptions,
    })


@accreditation_view_required(redirect_url=reverse_lazy(u'login'))  # If connected and and has a confirmed email address
def payment_view(request, subscription_name, product):
    """
    A view without template, which create the payment and redirect to Payplug's site

    :param request: Request object
    :param subscription_name: The subscription related to the payment
    :param product: The product related to the payment
    :return: Redirect to the Payplug's site or an error 404
    """
    subscription = get_object_or_404(Subscription, name=subscription_name)

    # Only with online sites
    return_url = request.build_absolute_uri(reverse("status"))
    cancel_url = request.build_absolute_uri(reverse("subscriptions"))
    notification_url = request.build_absolute_uri(reverse("notifications"))
    hosted_payment = {'return_url': return_url, 'cancel_url': cancel_url}

    # try/except 404
    try:
        product = subscription.products.get(name=product)
    except Product.DoesNotExist:
        return HttpResponseNotFound('<h1>Http 404</h1>')

    payment = create_classic_payment(request.user, subscription=subscription, product=product, data={
        'hosted_payment': hosted_payment,
        'notification_url': notification_url,
    })
    return HttpResponseRedirect(payment.hosted_payment.payment_url)


@csrf_exempt  # Error without. Possible to improve it?
def notifications_payplug_view(request):
    """
    A view without template, which receive Payplug's response by the notification_url, for the state of the payment.
    :param request: Request object
    :return: Code http 200
    """
    try:
        response = payplug.notifications.treat(request.body)  # Full api provide by payplug to manage the response
    except payplug.exceptions.PayplugError:
        return HttpResponse(400)
    else:
        update_payment(response)
    return HttpResponse(200)


def response_view(request):
    """
    A view for the payment's status

    :param request: Request object
    :return: Render of the view
    """
    template_name = "payment/notifications.html"
    payment = request.user.get_last_payment()
    return render(request, template_name, {
        'status': payment.status,
        'error_message': payment.error_message,
    })
