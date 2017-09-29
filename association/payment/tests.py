# from django.test import TestCase
import webbrowser

import payplug

payplug.set_secret_key('sk_test_5FVRtiAo2p1luWvHMmHa8z')


payment_data = {
  'amount': int(100),
  'currency': 'EUR',
  'customer': {
    'email': 'john.watson@example.net'
  },
  'hosted_payment': {
    'return_url': 'https://example.net/return?id=42710',
    'cancel_url': 'https://example.net/cancel?id=42710',
  },
  'notification_url': 'https://example.net/notifications?id=42710',
  'metadata': {
    'customer_id': 42710,
  },
}
payment = payplug.Payment.create(**payment_data)
payment_id = str(payment.id)

print(payment.hosted_payment.payment_url)
