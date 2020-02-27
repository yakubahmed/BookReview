from django.contrib import admin
from orders.models import Pizza, Pasta, Toppings, Salads, SubExtra, Subs, DinnerPlatters, Orders

# Register your models here.
myModels = [Pizza, Pasta, Toppings, Salads, SubExtra, Subs, DinnerPlatters, Orders]  # iterable list
admin.site.register(myModels)