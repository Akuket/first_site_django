from django.conf.urls import url

from .views import payment_view, subscription_view, notifications_payplug_view, error_view

urlpatterns = [
    url(r'^$', view=subscription_view, name="subscriptions"),
    url(r'^payment/(?P<subscription>.+)-(?P<product>.+)/$', view=payment_view, name="payment"),
    url(r'^notifications/$', view=notifications_payplug_view, name="notifications payplug"),
    url(r'^payment/(?P<payment_id>.+)/$', view=error_view, name="payment_error"),
]
