from datetime import datetime, timedelta, time

from account.models import PaymentsUser

today = datetime.now().date()
tomorrow = today + timedelta(1)
today_start = datetime.combine(today, time())
today_end = datetime.combine(tomorrow, time())

print(today)
print(tomorrow)
print(today_start)
print(today_end)

print(PaymentsUser.objects.filter(start__lte=today_end, end__gte=today_start).order_by("-date"))
