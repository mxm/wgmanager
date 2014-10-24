from django.db import models
from myauth.models import MyUser

from django.utils import timezone
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse

from core.util import first_day_of_month, last_day_of_month

class Community(models.Model):
    # TODO name should be unique for clarity?
    name = models.CharField(max_length=32)
    time = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(MyUser, related_name="members", blank=True)
    conf_sendmail = models.BooleanField(default=True)

    def get_bills(self):
        return Bill.objects.filter(community=self)

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
        return Shopping.objects.filter(shopping_day__range=[self.start, self.end])

    def get_payers(self):
        return Payer.objects.filter(bill=self)

    def get_stats(self):
        pass

    def get_dues(self):
        pass

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
    user = models.ForeignKey(MyUser)
    bill = models.ForeignKey(Bill, related_name="payers")
    fraction = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        unique_together = (('user', 'bill'),)

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
    user = models.ForeignKey(MyUser)
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
