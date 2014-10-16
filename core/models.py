from django.db import models
from myauth.models import MyUser

from datetime import datetime
from django.utils.translation import ugettext as _


class Bill(models.Model):
    name = models.CharField(max_length=1023)
    is_open = models.BooleanField(default=True)

class Payer(models.Model):
    user = models.ForeignKey(MyUser)
    bill = models.ForeignKey(Bill, related_name="payers")
    fraction = models.DecimalField(max_digits=3, decimal_places=2)

class Shop(models.Model):
    name = models.CharField(max_length=30)

class Tag(models.Model):
    name = models.CharField(max_length=30)

class Shopping(models.Model):
    user = models.ForeignKey(MyUser)
    time = models.DateField(default=datetime.now)
    place = models.ForeignKey(Shop, related_name="shoppings")
    expenses = models.DecimalField(max_digits=10,decimal_places=2)
    num_products = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name="tags")
    bill = models.ForeignKey(Bill, null=True, blank=True, related_name="shoppings")
    comment = models.CharField(max_length=1023,blank=True, null=True)

    def __str__(self):
        return _("%(expenses) with %(products) by %(user) at %(shop)") % {'expenses': self.expenses, 'user': self.user, 'products':           num_products, 'shop': self.shop}
