var choosenSub = [];
var choosenPizza =[]; 
var toppingsAmount = 0;
var priceChoosenPizza = 0;
var priceChoosenSub = 0;
window.choosenExtra = [];


if (window.localStorage.getItem('totalPriceCart')==null) {
    var totalPriceCart = 0;
} else {
    var totalPriceCart = window.localStorage.getItem('totalPriceCart');
};
if (JSON.parse(window.localStorage.getItem('shoppingCart'))==null) {
    var shoppingCartAll = []; 
} else {
    var shoppingCartAll = JSON.parse(window.localStorage.getItem('shoppingCart'));
};

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById("page-header").innerHTML === "Our Pizza Menu") {
        fillShoppingCartWithLocalStorage();
        if (window.localStorage.getItem('shoppingCart')!=null) {
            document.getElementById("placeOrder1").disabled=false;
        }
    } else if (document.getElementById("page-header").innerHTML === "Cart Items") {
        fillCheckOutCart();
    } else {
        console.log(3);
    };    
});

function fillShoppingCartWithLocalStorage () {
    var totalPriceCart = 0;
    for (i=0;i<shoppingCartAll.length;i++) {
        // Create new item for cart list
        const li = document.createElement('li');
        totalPriceCart = Number(totalPriceCart)+Number(shoppingCartAll[i]["price"]);
        li.innerHTML = shoppingCartAll[i]["description"];

        // Add new item to cart list
        document.querySelector('#shopping-cart-list').append(li);
    }
    document.getElementById('shopping-cart-total-modal').innerHTML = totalPriceCart;
    document.getElementById('shopping-cart-total').innerHTML = totalPriceCart;
};

function addPizzaToppings (pizza) {
    document.getElementById("select-pizza-topping-1").disabled=true;
    document.getElementById("select-pizza-topping-2").disabled=true;
    document.getElementById("select-pizza-topping-3").disabled=true;
    document.getElementById("select-pizza-topping-1").style.display = "none";
    document.getElementById("select-pizza-topping-2").style.display = "none";
    document.getElementById("select-pizza-topping-3").style.display = "none";
    
    toppingsAmount = pizza.getAttribute("data-amount");
    choosenPizza = pizza.getAttribute("data-description");
    priceChoosenPizza = pizza.getAttribute("data-price");

    if (toppingsAmount === "0") {
        document.getElementById("pizza_question").innerHTML = "Do you want to add a Regular pizza to your shopping cart?";
    } else {
        document.getElementById("pizza_question").innerHTML = "Which topping(s) would you like on your pizza?";
    };

    for (i = 0; i<toppingsAmount; i++) {
        var loopToppings = "select-pizza-topping-"+(i+1);
        var loopToppings2 = String(loopToppings);
        document.getElementById(loopToppings2).disabled = false;
        document.getElementById(loopToppings2).style.display = "";
    };
};

function myFunction(item) {
    var itemDescription = item.getAttribute("data-name");
    var itemPrice = item.getAttribute("data-price");
    priceChoosenSub = itemPrice;
    choosenSub = itemDescription;
};

function addExtra(choosenExtra) {
    window.choosenExtra = choosenExtra.value;
};

function sendToCartPizza() {
    var toppings = "";
    for (i = 0; i<toppingsAmount; i++) {
        var loopToppings = "select-pizza-topping-"+(i+1);
        var loopToppings2 = String(loopToppings);
        var e = document.getElementById(loopToppings2);
        var topping = e.options[e.selectedIndex].value;
        if (topping === "No Topping") {
            console.log("testttonnn");
        } else {
            toppings = toppings.concat(", "+topping);
        };
    };



    var choosenPizzaWithToppings = choosenPizza + toppings;

    totalPriceCart = Number(totalPriceCart) + Number(priceChoosenPizza);
    window.localStorage.setItem('totalPriceCart',totalPriceCart);
        
    document.getElementById('shopping-cart-total').innerHTML = totalPriceCart;
    document.getElementById('shopping-cart-total-modal').innerHTML = totalPriceCart;

    addToShoppingCartList(choosenPizzaWithToppings,priceChoosenPizza);
};

function sendToCartSub() {
    var subItemPrice = 0.5;
    if (window.choosenExtra.length === 0 || window.choosenExtra==="No Extras") {
        window.choosenExtra = "No Extras";
        subItemPrice = 0;
    }

    var itemDescription = "Sub "+choosenSub + ", with " + window.choosenExtra;
    var itemPrice = Number(priceChoosenSub) + Number(subItemPrice);
    
    totalPriceCart = Number(totalPriceCart) + Number(itemPrice);
    window.localStorage.setItem('totalPriceCart',totalPriceCart);
    
    document.getElementById('shopping-cart-total').innerHTML = totalPriceCart;
    document.getElementById('shopping-cart-total-modal').innerHTML = totalPriceCart;

    addToShoppingCartList(itemDescription, itemPrice);
};


function sendToCart(item) {
    var itemDescription = item.getAttribute("data-name");
    var itemPrice = item.getAttribute("data-price");
    
    
    totalPriceCart = Number(parseFloat(totalPriceCart) + parseFloat(itemPrice)).toFixed(2);
    window.localStorage.setItem('totalPriceCart',totalPriceCart);

    document.getElementById('shopping-cart-total').innerHTML = totalPriceCart;
    document.getElementById('shopping-cart-total-modal').innerHTML = totalPriceCart;

    addToShoppingCartList(itemDescription, itemPrice);
};


function addToShoppingCartList(description, price) {
    // Create new item for cart list
    const li = document.createElement('li');
    var price = price;
    li.innerHTML = description;

    document.getElementById("placeOrder1").disabled=false;

    shoppingCartAll.push({description:description, price:price}); 
    window.localStorage.setItem('shoppingCart', JSON.stringify(shoppingCartAll));

    //console.log(shoppingCartAll);
    // Add new item to cart list
    document.querySelector('#shopping-cart-list').append(li);
    

};


function clearCart(){
    
    window.localStorage.clear();
    document.getElementById("placeOrder1").disabled=true;
    document.getElementById('shopping-cart-total').innerHTML = 0;
    document.getElementById('shopping-cart-total-modal').innerHTML = 0;
    document.getElementById('shopping-cart-list').innerHTML ='';
    shoppingCartAll =[];
    totalPriceCart=0;
    priceChoosenSub = 0;
    choosenSub = [];
    
};

// payment ------------------------------------------

function fillCheckOutCart() {
    var totalPriceCart = 0;
    var shoppingCartString = '';
    for (i=0;i<shoppingCartAll.length;i++) {
        // Create new item for cart list
        const li = document.createElement('li');
        totalPriceCart = Number(totalPriceCart)+Number(shoppingCartAll[i]["price"]);
        li.innerHTML = shoppingCartAll[i]["description"];
        shoppingCartString = shoppingCartAll[i]["description"] + ' ; ' + shoppingCartString;
        
        document.getElementById('order_overview').value = shoppingCartString;
        document.getElementById('checkOutPrice').innerHTML = totalPriceCart;
        document.getElementById('order_price').value = totalPriceCart;
        // Add new item to cart list
        document.querySelector('#checkOutCart').append(li);
    }
};


/*
$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
});


*/