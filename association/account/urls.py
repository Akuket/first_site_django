from django.conf.urls import url
from django.contrib.auth.views import LogoutView

from .views import DashboardView, RegisterView, ResendEmailView, ForgotPasswordView, validate, ResetPasswordView, \
    ChangePasswordView, CustomLoginView

urlpatterns = [
    url(r'^$', view=DashboardView.as_view(), name="dashboard"),
    url(r'^login/$', view=CustomLoginView.as_view(), name="login"),
    url(r'^logout/$', view=LogoutView.as_view(), name="logout"),
    url(r'^register/$', view=RegisterView.as_view(), name="register"),
    url(r'^validate/(?P<token>[0-9A-Fa-f-]+)/$', view=validate, name='validate'),
    url(r'^resend_validate/$', view=ResendEmailView.as_view(), name='resend'),
    url(r'^forgot_password/$', view=ForgotPasswordView.as_view(), name="forgot"),
    url(r'^reset_password/(?P<token>[0-9A-Fa-f-]+)/$', view=ResetPasswordView.as_view(), name='reset_password'),
    url(r'^change_password/$', view=ChangePasswordView.as_view(), name="change_password"),
]
