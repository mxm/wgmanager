from django.contrib import admin

from core.models import Community, Shopping, Shop, Bill, Tag, Payer
from core.models import ShoppingListEntry, ChatEntry

admin.site.register(Community)
admin.site.register(Shopping)
admin.site.register(Shop)
admin.site.register(Bill)
admin.site.register(Tag)
admin.site.register(Payer)
admin.site.register(ShoppingListEntry)
admin.site.register(ChatEntry)
