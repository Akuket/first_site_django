from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^account/', include("account.urls")),
    url(r'^payment/', include("payment.urls")),
    url(r'^admin/', admin.site.urls, name="admin"),
]
