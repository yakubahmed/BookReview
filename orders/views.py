from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm

from orders.forms import SignUpFormt
from .models import Pizza, Toppings, Pasta, Salads, SubExtra, Subs, DinnerPlatters, Orders


def index(request):
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})
    context = {
        "user": request.user,
        "salads": Salads.objects.all(),
        "subs": Subs.objects.all(),
        "subextra":SubExtra.objects.all(),
        "pizzas":Pizza.objects.all(),
        "toppings":Toppings.objects.all(),
    }
    return render(request, "orders/menu.html", context)
    

def payment_view(request):
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})
    context = {
        "user": request.user,
        "orders":Toppings.objects.all(),
    }
    return render(request, "orders/payment.html", context)

def pay(request):
    print('RECEIVED REQUEST: ' +request.method) 
    if request.method == 'POST':
        order_description= request.POST.get('order_overview')
        order_price= request.POST.get('order_price') 
        print(order_description)
        print(order_price)
        Orders.objects.create(order_description=order_description ,order_price=order_price)
        return render(request, "orders/payment.html")
    else: #GET
        print('GET')
        return render(request, "orders/error.html")

def login_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "orders/login.html", {"message": "Invalid credentials."})
 
def logout_view(request):
    logout(request)
    return render(request, "orders/login.html", {"message": "Logged out."})

def signup_view(request):
    if request.method == 'POST':
        #form = UserCreationForm(request.POST)
        form = SignUpFormt(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = SignUpFormt()
    return render(request, 'orders/signup.html', {'form': form})

def error_view(request):
    return render(request, "orders/error.html")