from django.utils import timezone
import calendar

from decimal import Decimal, ROUND_UP

def first_day_of_month():
    date = timezone.now()
    return timezone.datetime(date.year, date.month, 1)

def last_day_of_month():
    date = timezone.now()
    (_weekday, numdays) = calendar.monthrange(date.year, date.month)
    return timezone.datetime(date.year, date.month, numdays)

# make sure expenses are covered when final amount cannot be divided by the number of payers
# problem: dues can be a cent too much
def round_up(decimal):
    return decimal.quantize(Decimal('.01'), rounding=ROUND_UP)
