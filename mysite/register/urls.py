from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from .views import DashboardView

app_name = 'register'
urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(template_name="register/login.html", redirect_authenticated_user=True),
        name="login"),
    url(r'^logout/$', view=LogoutView.as_view(), name="logout"),
    url(r'^dasboard/$', view=DashboardView.as_view(), name="dashboard"),
]
