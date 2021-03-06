from django.db import models, transaction
from django.db.models import Sum, Q

from django.core.exceptions import ValidationError

from django.utils import timezone
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse

from core import util
from core.util import first_day_of_month, last_day_of_month, get_month_name

from myauth.models import MyUser

class User(MyUser):
    class Meta:
        proxy = True

    def get_shoppings(self, community):
        return Shopping.objects.filter(user=self, community=community)

class Community(models.Model):
    # TODO name should be unique for clarity?
    name = models.CharField(max_length=32)
    time = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(User, related_name="members", blank=True)
    conf_sendmail = models.BooleanField(default=True)

    def get_bills(self):
        return Bill.objects.filter(community=self)

    def get_shoppings(self):
        return Shopping.objects.filter(community=self)

    def get_entries(self):
        return ShoppingListEntry.objects.filter(community=self, time_done=None)

    def get_messages(self):
        return ChatEntry.objects.filter(community=self)

    def get_absolute_url(self):
        return reverse('community', args=[self.id])

    def __str__(self):
        return self.name

class Bill(models.Model):
    community = models.ForeignKey(Community)
    start = models.DateField(default=first_day_of_month, db_index=True)
    end = models.DateField(default=last_day_of_month, db_index=True)
    is_special = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def get_shoppings(self):
        return Shopping.objects.filter(community=self.community, shopping_day__range=[self.start, self.end])

    def get_sum(self):
        return self.get_shoppings().aggregate(Sum('expenses'))['expenses__sum']

    def get_payers(self):
        return Payer.objects.filter(bill=self)

    def get_dues(self):
        payers = self.get_payers()
        num_payers = payers.__len__()
        total_expenses = self.get_sum()
        try:
            due_per_payer = util.round_up(total_expenses / num_payers)
        except:
            due_per_payer = 0
        dues = {}
        for payer in payers:
            expenses = payer.get_expenses(self)
            payer_due = util.round_up(payer.fraction * due_per_payer) - expenses
            dues[payer] = payer_due
        return dues

    def toggle_close(self):
        if not self.is_closed:
            # make out a bill / calculate dues
            # send mail
            pass
        self.is_closed = not self.is_closed
        self.save()

    def get_conflicting_bills(self):
        community_bills = self.community.get_bills()
        conflicting_bills = community_bills.filter(
            Q(start__lte=self.start) | Q(start__lte=self.end)).filter(
            Q(end__gte=self.start)   | Q(end__gte=self.end)
        )
        # we need to filter out ourself (i.e. if we change a bill range)
        # figure out if we are an existing object
        if self.id:
            return conflicting_bills.exclude(id=self.id)
        else:
            return conflicting_bills

    def clean(self):
        if not self.start <= self.end:
            raise ValidationError(_('Start date must be before or on end date'))
        if self.get_conflicting_bills().exists():
            raise ValidationError(_('There is a bill overlaping with this bill'))

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.get_conflicting_bills().exists():
            # this is a very unlikely case where two users create bills at the same time
            # which are in conflict with each other. it's ok to fail here, the user can
            # try again.
            raise Exception
        else:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('bill', args=[self.community.id, self.id])

    def __str__(self):
        # display month year if bill covers a whole month
        if self.start.day == first_day_of_month(self.start).day and self.end.day == last_day_of_month(self.end).day:
            return get_month_name(self.start.month) + " " + str(self.start.year)
        else:
            return str(self.start) + " - " + str(self.end)


class Payer(models.Model):
    user = models.ForeignKey(User)
    bill = models.ForeignKey(Bill, related_name="payers")
    fraction = models.DecimalField(default=1.0, max_digits=3, decimal_places=2)

    class Meta:
        unique_together = (('user', 'bill'),)

    def get_expenses(self, bill):
        shoppings = bill.get_shoppings().filter(user=self.user)
        user_expenses = shoppings.aggregate(Sum('expenses'))['expenses__sum']
        return user_expenses if user_expenses != None else 0

    def clean(self):
        if hasattr(self, 'user') and Payer.objects.filter(user=self.user, bill=self.bill).exists():
            raise ValidationError(_("User already added to this bill"))

    def get_absolute_url(self):
        return self.bill.get_absolute_url()

    def __str__(self):
        return _("Bill '%(bill)s': %(user)s with fraction %(fraction)s") % {'bill': self.bill, 'user': self.user, 'fraction': self.fraction}

class Shop(models.Model):
    name = models.CharField(max_length=30)
    community = models.ForeignKey(Community)
    visible = models.BooleanField(default=True)

    class Meta:
        unique_together = (('name', 'community'),)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30)
    community = models.ForeignKey(Community)
    visible = models.BooleanField(default=True)

    class Meta:
        unique_together = (('name', 'community'),)

    def __str__(self):
        return self.name

class Shopping(models.Model):
    user = models.ForeignKey(User)
    community = models.ForeignKey(Community)
    time = models.DateTimeField(default=timezone.now)
    shopping_day = models.DateField(default=timezone.now, db_index=True)
    shop = models.ForeignKey(Shop, related_name="shoppings")
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    num_products = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name="tags")
    #bill = models.ForeignKey(Bill, null=True, blank=True, related_name="shoppings")
    billing = models.BooleanField(default=True)
    comment = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ["-shopping_day"]

    def clean(self):
        if Bill.objects.filter(
                start__lte=self.shopping_day, end__gte=self.shopping_day,
                is_closed=True
        ).exists():
            raise ValidationError(_('You cannot add or modify a shopping of a closed bill'))

    def get_absolute_url(self):
        return reverse('shopping', args=[self.community.id, self.id])

    def __str__(self):
        return _("%(expenses)s with %(products)d items by %(user)s at %(shop)s") % {'expenses': self.expenses, 'user': self.user, 'products': self.num_products, 'shop': self.shop}

class ShoppingListEntry(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(User)
    subject = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True)
    time_created = models.DateTimeField(default=timezone.now)
    time_done = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject

class ChatEntry(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(User)
    message = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.user) + ": " + self.message
