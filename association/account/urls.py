from django.conf.urls import url
from django.contrib.auth.views import LogoutView

from .views import DashboardView, RegisterView, ResendEmailView, ForgotPasswordView, validate, ResetPasswordView, \
    ChangePasswordView, CustomLoginView, DisplayPayments, UpdateUserFields, DownloadPayment, unsuscribe, SeeUserData

urlpatterns = [
    url(r'^$', view=DashboardView.as_view(), name="dashboard"),
    url(r'^login/$', view=CustomLoginView.as_view(), name="login"),
    url(r'^logout/$', view=LogoutView.as_view(), name="logout"),
    url(r'^update/$', view=UpdateUserFields.as_view(), name="update"),
    url(r'^register/$', view=RegisterView.as_view(), name="register"),
    url(r'^info/$', view=SeeUserData.as_view(), name="personnal_info"),
    url(r'^unsuscribe/$', view=unsuscribe, name="unsuscribe"),
    url(r'^validate/(?P<token>[0-9A-Fa-f-]+)/$', view=validate, name='validate'),
    url(r'^resend_validate/$', view=ResendEmailView.as_view(), name='resend'),
    url(r'^forgot_password/$', view=ForgotPasswordView.as_view(), name="forgot"),
    url(r'^reset_password/(?P<token>[0-9A-Fa-f-]+)/$', view=ResetPasswordView.as_view(), name='reset_password'),
    url(r'^change_password/$', view=ChangePasswordView.as_view(), name="change_password"),
    url(r'^display_payments/$', view=DisplayPayments.as_view(), name="display_payments"),
    url(r'^download/(?P<pk>.+)/$', view=DownloadPayment.as_view(), name="download"),
]
