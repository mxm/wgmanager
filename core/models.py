from django.db import models
from myauth.models import MyUser

from django.utils import timezone
from django.utils.translation import ugettext as _


class Bill(models.Model):
    name = models.CharField(max_length=1023)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payer(models.Model):
    # TODO user should be unique per bill
    user = models.ForeignKey(MyUser)
    bill = models.ForeignKey(Bill, related_name="payers")
    fraction = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return _("Bill '%(bill)s': %(user)s with fraction %(fraction)s") % {'bill': self.bill, 'user': self.user, 'fraction': self.fraction}

class Shop(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Shopping(models.Model):
    user = models.ForeignKey(MyUser)
    time = models.DateField(default=timezone.now)
    shop = models.ForeignKey(Shop, related_name="shoppings")
    expenses = models.DecimalField(max_digits=10,decimal_places=2)
    num_products = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name="tags")
    bill = models.ForeignKey(Bill, null=True, blank=True, related_name="shoppings")
    comment = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return _("%(expenses)s with %(products)d items by %(user)s at %(shop)s") % {'expenses': self.expenses, 'user': self.user, 'products': self.num_products, 'shop': self.shop}
