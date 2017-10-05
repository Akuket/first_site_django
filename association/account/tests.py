from datetime import datetime, timedelta, time

from models import PaymentsUser


today_start = datetime.combine(datetime.now().date(), time())
today_end = datetime.combine(datetime.now().date() + timedelta(1), time())

print(today_start)
print(today_end)

e.PaymentsUser.objects.filter(date__range=(today_start, today_end))