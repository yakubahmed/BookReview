from django.db import models

# to import in shell following comamnd >> from orders.models import Pizza, Toppings, Pasta, Salads, SubExtra, Subs, DinnerPlatters

# Create your models here.

class Toppings(models.Model):
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description

class Pizza(models.Model):
    description = models.CharField(max_length=100)
    PIZZA_SIZES = (
        ('S', 'Small'),
        ('L', 'Large'),
    )
    PIZZA_TYPES = (
        ('R', 'Regular'),
        ('S', 'Sicilian'),
    )
    PIZZA_TOPPINGS = (
        (0, 0),
        (1, 1),
        (2, 2),
    )
    size = models.CharField(max_length=1, choices=PIZZA_SIZES, default="S")
    pizza_type = models.CharField(max_length=1, choices=PIZZA_TYPES, default="R")
    pizza_toppings = models.IntegerField(choices=PIZZA_TOPPINGS, default=0)
    price = models.FloatField()
    toppings = models.ManyToManyField(Toppings)

    def __str__(self):
        return self.description


class Pasta(models.Model):
    description = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return self.description

class Salads(models.Model):
    description = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return self.description

class SubExtra (models.Model):
    description = models.CharField(max_length=100)
    price = models.FloatField()
    
    def __str__(self):
        return self.description

class Subs (models.Model):
    description = models.CharField(max_length=100)
    SUB_SIZES = (
        ('S', 'Small'),
        ('L', 'Large'),
    )
    size = models.CharField(max_length=1, choices=SUB_SIZES, default="S")
    price = models.FloatField(default=6.50)
    extras = models.ManyToManyField(SubExtra)

    def __str__(self):
        return self.description

class DinnerPlatters(models.Model):
    description = models.CharField(max_length=100) 
    PLATTER_SIZES = (
        ('S', 'Small'),
        ('L', 'Large'),
    )
    size = models.CharField(max_length=1, choices=PLATTER_SIZES)
    price = models.FloatField()

    def __str__(self):
        return self.description

class Orders(models.Model): #Todo migreren
    #order_id = models.IntegerField()   # ToDo kijken of je met many to many relationships kan fixen 
    order_description = models.TextField()
    order_price = models.FloatField()