from django.db import models
from django.db.models import Sum

from django.utils import timezone
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse

from core import util
from core.util import first_day_of_month, last_day_of_month

from myauth.models import MyUser

class User(MyUser):
    class Meta:
        proxy = True

    def get_shoppings(self, community):
        return Shoppings.objects.filter(user=self, community=community)

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
    start = models.DateField(default=first_day_of_month)
    end = models.DateField(default=last_day_of_month)
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


    def close(self):
        if not self.closed:
            # make out a bill / calculate dues
            # send mail
            self.is_closed = True

    def get_absolute_url(self):
        return reverse('bill', args=[self.community.id, self.id])

    def __str__(self):
        return str(self.start) + " - " + str(self.end)


class Payer(models.Model):
    user = models.ForeignKey(User)
    bill = models.ForeignKey(Bill, related_name="payers")
    fraction = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        unique_together = (('user', 'bill'),)

    def get_expenses(self, bill):
        shoppings = bill.get_shoppings().filter(user=self.user)
        user_expenses = shoppings.aggregate(Sum('expenses'))['expenses__sum']
        return user_expenses if user_expenses != None else 0


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
    shopping_day = models.DateField(default=timezone.now)
    shop = models.ForeignKey(Shop, related_name="shoppings")
    expenses = models.DecimalField(max_digits=10, decimal_places=2)
    num_products = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name="tags")
    #bill = models.ForeignKey(Bill, null=True, blank=True, related_name="shoppings")
    billing = models.BooleanField(default=True)
    comment = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ["-shopping_day"]

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
