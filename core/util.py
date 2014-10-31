from django.utils import timezone
import calendar

from django.utils.translation import ugettext as _

from decimal import Decimal, ROUND_UP

def first_day_of_month(date=None):
    if not date:
        date = timezone.now()
    return timezone.datetime(date.year, date.month, 1)

def last_day_of_month(date=None):
    if not date:
        date = timezone.now()
    (_weekday, numdays) = calendar.monthrange(date.year, date.month)
    return timezone.datetime(date.year, date.month, numdays)

months = [_("January"),
          _("February"),
          _("March"),
          _("April"),
          _("May"),
          _("June"),
          _("July"),
          _("August"),
          _("September"),
          _("October"),
          _("November"),
          _("December")]

def get_month_name(month):
    return months[month-1]

# make sure expenses are covered when final amount cannot be divided by the number of payers
# problem: dues can be a cent too much
def round_up(decimal):
    return decimal.quantize(Decimal('.01'), rounding=ROUND_UP)
