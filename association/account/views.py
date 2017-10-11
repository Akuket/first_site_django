from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView
from django.views.generic.edit import UpdateView
from django_weasyprint import WeasyTemplateResponseMixin

from .forms import CustomUserForm, ResendEmailForm, ForgotPasswordForm
from .models import User, ValidateUser, ResetUserPassword, PaymentsUser
from .email import send_register_mail, send_reset_password_mail
from .api import AnonymousRequiredMixin, accreditation_view_required


class CustomLoginView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        if self.request.user.is_staff:
            return HttpResponseRedirect(reverse_lazy("admin:index"))
        return HttpResponseRedirect(self.get_success_url())


class DashboardView(TemplateView):
    template_name = "account/dashboard.html"


class RegisterView(AnonymousRequiredMixin, CreateView):
    form_class = CustomUserForm
    template_name = "account/register.html"
    success_url = reverse_lazy(u"dashboard")

    def form_valid(self, form):
        self.object = form.save()
        validate_user = ValidateUser(user=self.object)
        validate_user.save()
        link = self.request.build_absolute_uri(reverse("validate", kwargs={'token': validate_user.token}))
        send_register_mail(link, self.object.username, self.object.email, "test")
        return HttpResponseRedirect(self.get_success_url())


class UpdateUserFields(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['name', 'first_name', 'address','postcode','city','country','email',]
    template_name = "account/update_user_fields.html"
    success_url = reverse_lazy(u"dashboard")

    def get_object(self):
        return self.request.user


class ResendEmailView(AnonymousRequiredMixin, FormView):
    form_class = ResendEmailForm
    template_name = "account/resend_email.html"
    success_url = reverse_lazy(u"dashboard")

    def form_valid(self, form):
        try:
            user = User.objects.get(email=form.cleaned_data["email"])
        except(KeyError, User.DoesNotExist):
            return HttpResponseRedirect(reverse_lazy(u"resend"))
        else:
            token = ValidateUser.objects.get(user=user).token
            link = self.request.build_absolute_uri(reverse("validate", kwargs={'token': token}))
            send_register_mail(link, user.username, user.email, "test")
        return HttpResponseRedirect(self.get_success_url())


class ForgotPasswordView(AnonymousRequiredMixin, FormView):
    form_class = ForgotPasswordForm
    template_name = "account/forgot_password.html"
    success_url = reverse_lazy(u"login")

    def form_valid(self, form):
        try:
            user1 = User.objects.get(username=form.cleaned_data["username"])
            user2 = User.objects.get(email=form.cleaned_data["email"])
        except(KeyError, User.DoesNotExist):
            messages.error(self.request, 'Please correct the error below.')
        else:
            if user1 == user2:
                resend = ResetUserPassword(user=user1)
                resend.save()
                link = self.request.build_absolute_uri(reverse("reset_password", kwargs={'token': resend.token}))
                send_reset_password_mail(link, user1.username, user1.email, "test")
                return HttpResponseRedirect(self.get_success_url())
            else:
                messages.error(self.request, 'Please correct the error below.')

        return render(self.request, reverse_lazy(u"forgot"))


class ResetPasswordView(FormView):
    form_class = SetPasswordForm
    template_name = "account/forgot_password.html"
    success_url = reverse_lazy(u"login")

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ResetPasswordView, self).get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if "token" in kwargs:
            token = kwargs["token"]
            try:
                self.user = ResetUserPassword.objects.get(token=token).user
            except(KeyError, ResetUserPassword.DoesNotExist):
                return HttpResponseRedirect(reverse_lazy(u"dashboard"))
            else:
                return super(ResetPasswordView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy(u"dashboard"))

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy(u"login"))


class ChangePasswordView(PasswordChangeView):
    template_name = "account/change_password.html"
    success_url = reverse_lazy(u"dashboard")

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse_lazy(u"dashboard"))


class DisplayPayments(ListView):
    template_name = "account/display_payments.html"
    context_object_name = "payments"
    paginate_by = 1

    def get_queryset(self):
        return self.request.user.get_all_payments()


class DownloadPayment(WeasyTemplateResponseMixin, DetailView):
    template_name = "payment/facture.html"
    queryset = PaymentsUser.objects.all()
    context_object_name = "payment"


# If connected and no validate email only
@accreditation_view_required(perm=0, strict=True, redirect_url=reverse_lazy(u"dashboard"))
def validate(request, token):
    try:
        validate_user = ValidateUser.objects.get(token=token)
    except(KeyError, ValidateUser.DoesNotExist):
        return HttpResponseRedirect(reverse_lazy(u"dashboard"))
    else:
        user = validate_user.user
        user.accreditation = 1
        user.save()
    return HttpResponseRedirect(reverse_lazy(u"login"))


@accreditation_view_required(perm=2, redirect_url=reverse_lazy(u"dashboard"))
def unsuscribe(request):
    request.user.unsuscribe()
    return HttpResponseRedirect(reverse_lazy(u"logout"))
