from django.conf.urls import url

from .views import payment_view, subscription_view, notifications_payplug_view

urlpatterns = [
    url(r'^$', view=subscription_view, name="subscriptions"),
    url(r'^payment/(?P<subscription>.+)-(?P<product>.+)/$', view=payment_view, name="payment"),
    url(r'^notifications/$', view=notifications_payplug_view, name="notifications"),
]
