from django.utils import timezone
import calendar

def first_day_of_month():
    date = timezone.now()
    return timezone.datetime(date.year, date.month, 1)

def last_day_of_month():
    date = timezone.now()
    (_weekday, numdays) = calendar.monthrange(date.year, date.month)
    return timezone.datetime(date.year, date.month, numdays)
