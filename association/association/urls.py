from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import redirect

urlpatterns = [
    url(r'^account/', include("account.urls")),
    url(r'^payment/', include("payment.urls")),
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^$', lambda _: redirect('account/'), name='dashbaord'),
]
