import datetime
from collections import namedtuple

from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from account.models import User, ValidateUser, ResetUserPassword, PaymentsUser, SaveCardUser
from payment.models import Subscription, Product
from .api import AnonymousRequiredMixin, AccreditationViewRequiredMixin, accreditation_view_required

Login = reverse(u"login")
Dashboard = reverse(u"dashboard")
Register = reverse(u"register")
Update = reverse(u"update")
Info = reverse(u"personnal_info")
Resend = reverse(u"resend")
Forgot = reverse(u"forgot")
Change = reverse(u"change_password")
Payments = reverse(u"display_payments")
Unsubscribe = reverse(u"unsubscribe")


class FakeResponse:
    status_code = 200


class FakeBaseView:
    @staticmethod
    def dispatch(_):
        response = FakeResponse()
        return response


class FakeAnonymousView(AnonymousRequiredMixin, FakeBaseView):
    pass


class FakeAccreditationViewRequiredView(AccreditationViewRequiredMixin, FakeBaseView):
    pass


class FakeAccreditationViewRequiredView1(AccreditationViewRequiredMixin, FakeBaseView):
    strict = True


class FakeAccreditationViewRequiredView2(AccreditationViewRequiredMixin, FakeBaseView):
    raise_exception = True


class FakeAccreditationViewRequiredView3(AccreditationViewRequiredMixin, FakeBaseView):
    strict = True
    raise_exception = True


class BuildAbsoluteUri:
    def __call__(self, *args, **kwargs):
        pass


class GetFullPath:
    def __call__(self, *args, **kwargs):
        pass


class Request:
    def __init__(self, user):
        self.user = user
        self.build_absolute_uri = BuildAbsoluteUri()
        self.get_full_path = GetFullPath()


def fake_view(request, perm=1, strict=False, redirect_url=None, raise_exception=False):
    @accreditation_view_required(perm=perm, strict=strict, redirect_url=redirect_url, raise_exception=raise_exception)
    def fake_view_response(_):
        return FakeResponse()

    return fake_view_response(request)


_User = namedtuple("User", ("is_authenticated", "accreditation"))


class TestAnonymousMixin(TestCase):
    def test_with_login_user(self):
        view = FakeAnonymousView()
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 302)

    def test_with_anonymous_user(self):
        view = FakeAnonymousView()
        request = Request(user=_User(is_authenticated=False, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)


class TestAccreditationViewRequiredMixin(TestCase):
    def test_basic(self):
        view = FakeAccreditationViewRequiredView()
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_basic_with_no_accreditation(self):
        view = FakeAccreditationViewRequiredView()
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 302)

    def test_basic_with_more_accreditation(self):
        view = FakeAccreditationViewRequiredView()
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_with_strict(self):
        view = FakeAccreditationViewRequiredView1()
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_strict_with_no_accreditation(self):
        view = FakeAccreditationViewRequiredView1()
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 302)

    def test_strict_with_more_accreditation(self):
        view = FakeAccreditationViewRequiredView1()
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 302)

    def test_raise_exception_with_accreditation(self):
        view = FakeAccreditationViewRequiredView2()
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_with_no_accreditation(self):
        view = FakeAccreditationViewRequiredView2()
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_raise_exception_with_more_accreditation(self):
        view = FakeAccreditationViewRequiredView2()
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_and_strict(self):
        view = FakeAccreditationViewRequiredView3()
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_and_strict_with_no_accreditation(self):
        view = FakeAccreditationViewRequiredView3()
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)

    def test_raise_exception_and_strict_with_more_accreditation(self):
        view = FakeAccreditationViewRequiredView3()
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        with self.assertRaises(PermissionDenied):
            view.dispatch(request)


class TestAccreditationViewRequiredDecorator(TestCase):
    def test_basic(self):
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = fake_view(request)
        self.assertEqual(response.status_code, 200)

    def test_basic_with_no_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        response = fake_view(request)
        self.assertEqual(response.status_code, 302)

    def test_basic_with_more_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = fake_view(request)
        self.assertEqual(response.status_code, 200)

    def test_strict(self):
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = fake_view(request, strict=True)
        self.assertEqual(response.status_code, 200)

    def test_strict_with_no_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        response = fake_view(request, strict=True)
        self.assertEqual(response.status_code, 302)

    def test_strict_with_more_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = fake_view(request, strict=True)
        self.assertEqual(response.status_code, 302)

    def test_raise_exception(self):
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = fake_view(request, raise_exception=True)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_with_no_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        with self.assertRaises(PermissionDenied):
            fake_view(request, raise_exception=True)

    def test_raise_exception_with_more_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = fake_view(request, raise_exception=True)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_and_strict(self):
        request = Request(user=_User(is_authenticated=True, accreditation=1))
        response = fake_view(request, raise_exception=True)
        self.assertEqual(response.status_code, 200)

    def test_raise_exception_and_strict_with_no_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=0))
        with self.assertRaises(PermissionDenied):
            fake_view(request, raise_exception=True)

    def test_raise_exception_and_strict_with_more_accreditation(self):
        request = Request(user=_User(is_authenticated=True, accreditation=2))
        response = fake_view(request, raise_exception=True)
        self.assertEqual(response.status_code, 200)

    def test_additional(self):
        request = Request(user=_User(is_authenticated=False, accreditation=2))
        response = fake_view(request, perm=0)
        self.assertEqual(response.status_code, 200)

    def test_additional1(self):
        request = Request(user=_User(is_authenticated=False, accreditation=2))
        response = fake_view(request, perm=2)
        self.assertEqual(response.status_code, 302)


class TestCustomLoginView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        response = self.client.get(Login)
        self.assertEqual(response.status_code, 200)

    def test_post_valid(self):
        response = self.client.post(Login, data={"username": "guillaume", "password": "passpass"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)

    def test_post_invalid(self):
        response = self.client.post(Login, data={"username": "test", "password": "a"})
        self.assertEqual(response.status_code, 200)

    def test_post_superuser(self):
        superuser = User(username="test", email="test@test.com", accreditation=1, is_staff=True)
        superuser.set_password('passpass')
        superuser.save()

        response = self.client.post(Login, data={"username": "test", "password": "passpass"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(u"admin:index"))


class TestDashboardView(TestCase):
    def test_get(self):
        response = self.client.get(Dashboard)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(Dashboard)
        self.assertEqual(response.status_code, 405)

    def test_post_args(self):
        response = self.client.post(Dashboard, data={"username": "test", "password": "passpass"})
        self.assertEqual(response.status_code, 405)


class TestRegisterView(TestCase):
    def test_get(self):
        response = self.client.get(Register)
        self.assertEqual(response.status_code, 200)

    def test_post_invalid(self):
        response = self.client.post(Register)
        self.assertEqual(response.status_code, 200)

    def test_post_valide(self):
        data = {"username": "test", "email": "te@test.com", "password1": "passpass", "password2": "passpass"}
        response = self.client.post(Register, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)


class TestUpdateUserFields(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.get(Update)
        self.assertEqual(response.status_code, 200)

    def test_post_invalid(self):
        self.client.login(username="guillaume", password="passpass")
        data = {"name": "test"}
        response = self.client.post(Update, data=data)
        self.assertEqual(response.status_code, 200)

    def test_post_valid(self):
        self.client.login(username="guillaume", password="passpass")
        data = {'name': "g", 'first_name': "c", 'address': "a", 'postcode': 2, 'city': "t", 'country': "e",
                'email': "a@b.com"}
        response = self.client.post(Update, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)


class TestSeeUserData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.get(Info)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(Info)
        self.assertEqual(response.status_code, 302)

    def test_post_args(self):
        response = self.client.post(Dashboard, data={"username": "test", "password": "passpass"})
        self.assertEqual(response.status_code, 405)


class TestResendEmailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

        ValidateUser.objects.create(user=cls.user)

    def test_get(self):
        response = self.client.get(Resend)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(Resend, data={"email": self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)

    def test_post_invalid(self):
        response = self.client.post(Resend, data={"email": "c@t.com"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Resend)


class TestForgotPasswordView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        response = self.client.get(Forgot)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(Forgot, data={"username": "guillaume", "email": "te@test.com", })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Login)

    def test_post_invalid(self):
        response = self.client.post(Forgot, data={"username": "guil", "email": "te@tet.com", })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Forgot)


class TestResetPasswordView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

        cls.validate = ResetUserPassword.objects.create(user=cls.user)
        cls.path = reverse(u"reset_password", kwargs={"token": cls.validate.token})

    def test_get_no_args(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse(u"reset_password"))

    def test_get(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_get_invalid(self):
        path = reverse(u"reset_password", kwargs={"token": "a"})
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)

    def test_post(self):
        response = self.client.post(self.path, data={"new_password1": "mdpaupif", "new_password2": "mdpaupif"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Login)

        self.client.login(username="guillaume", password="passpass")
        self.assertEqual(self.client.cookies, {})

        self.client.login(username="guillaume", password="mdpaupif")
        self.assertNotEqual(self.client.cookies, {})

    def test_post_invalid(self):
        response = self.client.post(self.path, data={"new_password1": "testt", "new_password2": "testt"})
        self.assertEqual(response.status_code, 200)


class TestChangePasswordView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.get(Change)
        self.assertEqual(response.status_code, 200)

    def test_post_no_args(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.post(Change)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.post(Change, data={"old_password": "passpass", "new_password1": "mdpaupif",
                                                  "new_password2": "mdpaupif"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)

        self.client.logout()

        self.client.login(username="guillaume", password="passpass")
        self.assertEqual(self.client.cookies, {})

        self.client.login(username="guillaume", password="mdpaupif")
        self.assertNotEqual(self.client.cookies, {})

    def test_post_invalid(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.post(Change, data={"new_password1": "testt", "new_password2": "testt"})
        self.assertEqual(response.status_code, 200)


class TestDisplayPayments(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=1)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_get(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.get(Payments)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username="guillaume", password="passpass")
        response = self.client.post(Payments)
        self.assertEqual(response.status_code, 405)


class TestValidate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=0)
        cls.user.set_password('passpass')
        cls.user.save()

        cls.validate = ValidateUser.objects.create(user=cls.user)
        cls.path = reverse(u"validate", kwargs={"token": cls.validate.token})

    def test_get_no_args(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse(u"validate"))

    def test_get(self):
        response = self.client.get(self.path)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Login)
        self.assertEqual(self.user.accreditation, 1)

    def test_get_invalid(self):
        response = self.client.get(reverse(u"validate", kwargs={"token": "a"}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Dashboard)

    def test_post(self):
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Login)


class TestUnsubscribe(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid", price=120, tva=20,
                                    subscription=subscription, product=product, user=cls.user)

        cls.card = SaveCardUser.objects.create(first_name="g", last_name="t", card_id="g", card_exp_date=date,
                                               card_available=True, user=cls.user)

    def setUp(self):
        self.client.login(username="guillaume", password="passpass")

    def test_get(self):
        response = self.client.get(Unsubscribe)
        self.user.refresh_from_db()
        self.card.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(u"logout"))
        self.assertEqual(self.user.accreditation, 1)
        self.assertEqual(self.card.card_available, False)

    def test_post(self):
        response = self.client.post(Unsubscribe)
        self.user.refresh_from_db()
        self.card.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(u"logout"))
        self.assertEqual(self.user.accreditation, 1)
        self.assertEqual(self.card.card_available, False)


class TestUserTestAnyPaymentValide(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_invalid(self):
        check = self.user.test_any_payment_valide()
        self.assertEqual(check, False)

    def test_valid(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid", price=120, tva=20,
                                    subscription=subscription, product=product, user=self.user)

        check = self.user.test_any_payment_valide()
        self.assertEqual(check, True)


class TestGetLastPayment(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_valid(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        payment = PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid",
                                              price=120, tva=20, subscription=subscription, product=product,
                                              user=self.user)

        check = self.user.get_last_payment()

        self.assertEqual(payment, check)

    def test_valid_2_payments(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid",
                                    price=120, tva=20, subscription=subscription, product=product, user=self.user)
        payment = PaymentsUser.objects.create(reference="b", date=date, subscribed_until=end, status="is_paid",
                                              price=120, tva=20, subscription=subscription, product=product,
                                              user=self.user)
        check = self.user.get_last_payment()
        self.assertEqual(check, payment)

    def test_invalid(self):
        check = self.user.get_last_payment()
        self.assertEqual(check, None)


class TestGetLastValidatePayment(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_valid(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        payment = PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid",
                                              price=120, tva=20, subscription=subscription, product=product,
                                              user=self.user)

        check = self.user.get_last_validate_payment()
        self.assertEqual(check, payment)

    def test_valid_2_payments(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid",
                                    price=120, tva=20, subscription=subscription, product=product, user=self.user)
        payment = PaymentsUser.objects.create(reference="b", date=date, subscribed_until=end, status="is_paid",
                                              price=120, tva=20, subscription=subscription, product=product,
                                              user=self.user)
        check = self.user.get_last_validate_payment()
        self.assertEqual(check, payment)

    def test_invalid(self):
        check = self.user.get_last_validate_payment()
        self.assertEqual(check, None)


class TestGetLastValidateCard(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_valid(self):
        date = datetime.date.today() + datetime.timedelta(1)
        card = SaveCardUser.objects.create(first_name="g", last_name="t", card_id="g", card_exp_date=date,
                                           card_available=True, user=self.user)

        check = self.user.get_last_validate_card()
        self.assertEqual(check, card)

    def test_valid_2_cards(self):
        date = datetime.date.today() + datetime.timedelta(10)

        SaveCardUser.objects.create(first_name="g", last_name="t", card_id="g", card_exp_date=date, card_available=True,
                                    user=self.user)
        card = SaveCardUser.objects.create(first_name="g", last_name="t", card_id="g", card_exp_date=date,
                                           card_available=True, user=self.user)

        check = self.user.get_last_validate_card()
        self.assertEqual(check, card)

    def test_invalid(self):
        check = self.user.get_last_validate_card()
        self.assertEqual(check, None)
        self.assertEqual(self.user.accreditation, 1)


class TestHtCost(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="guillaume", email="te@test.com", accreditation=2)
        cls.user.set_password('passpass')
        cls.user.save()

    def test_basic(self):
        date = datetime.date.today()
        end = date + datetime.timedelta(10)

        subscription = Subscription.objects.create(name="gold", description="test")
        product = Product.objects.create(name="test", description="rien", price=120, tva=20, ht=100,
                                         recurrent=True, duration=50, subscription=subscription)
        payment = PaymentsUser.objects.create(reference="a", date=date, subscribed_until=end, status="is_paid",
                                              price=120, tva=20, subscription=subscription, product=product,
                                              user=self.user)

        self.assertEqual(payment.ht_cost, 100)
