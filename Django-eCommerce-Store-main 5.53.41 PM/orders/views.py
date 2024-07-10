import json
import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.contrib import messages


from cart.models import CartItem, Cart
from cart.views import _cart_id
from django.core.exceptions import ObjectDoesNotExist
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from shop.models import Product


@login_required(login_url = 'accounts:login')
def payment_method(request):
    return render(request, 'shop/orders/payment_method.html',)


@login_required(login_url = 'accounts:login')
def checkout(request,total=0, total_price=0, quantity=0, cart_items=None):
    tax = 0.00
    handing = 0.00
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        total = total_price + 10

    except ObjectDoesNotExist:
        pass # just ignore

    
    tax = round(((2 * total_price)/100), 2)
    grand_total = total_price + tax
    handing = 15.00
    total = float(grand_total) + handing
    
    context = {
        'total_price': total_price,
        'quantity': quantity,
        'cart_items':cart_items,
        'handing': handing,
        'vat' : tax,
        'order_total': total,
    }
    return render(request, 'shop/orders/checkout/checkout.html', context)


from decimal import Decimal

@login_required(login_url='accounts:login')
def payment(request, total=Decimal('0'), quantity=0):
    current_user = request.user
    handling = Decimal('15.00')  # Using Decimal for monetary values
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('shop:shop')

    grand_total = Decimal('0')
    tax = Decimal('0')
    for cart_item in cart_items:
        total += Decimal(cart_item.product.price) * cart_item.quantity  # Converting to Decimal

    tax = ((Decimal('2') * total) / Decimal('100')).quantize(Decimal('0.01'))  # Rounding tax to two decimal places

    grand_total = total + tax
    total_amount = grand_total + handling
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.odered_Product = form.cleaned_data['odered_Product']
            data.payment_method = form.cleaned_data['payment_method']
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = total_amount  # Assigning total_amount instead of total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # Generate order number
            yr = datetime.date.today().strftime('%Y')
            dt = datetime.date.today().strftime('%d')
            mt = datetime.date.today().strftime('%m')
            current_date = yr + mt + dt
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=True, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'handling': handling,
                'vat': tax,
                'order_total': total_amount,
            }
            return render(request, 'shop/orders/checkout/payment.html', context)
        else:
            messages.error(request, 'Your information is not valid')
            return redirect('orders:checkout')
            
    else:
        return redirect('shop:shop')



def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=True, order_number=body['orderID'])
    
    # Store transation details inside payment model 
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        status = body['status'],
        amount_paid = order.order_total,
    )
    
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # Move the cart item to OrderProduct table 
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        # add variation to OrderProduct table
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        
        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear Cart 
    CartItem.objects.filter(user=request.user).delete()

    
    # Send order recieved email to cutomer 
    #subject = 'Thank you for your order!'
    #message = render_to_string('shop/orders/checkout/payment_recieved_email.html', {
    #    'user': request.user,
    #    'order':order,
    #})
    #to_email = request.user.email
    #send_email = EmailMessage(subject, message, to=[to_email])
    #send_email.send()
#
    #
    ## Send order recieved email to admin account 
    #subject = 'Thank you for your order!'
    #message = render_to_string('shop/orders/checkout/payment_recieved_email.html', {
    #    'user': request.user,
    #    'order':order,
    #})
    #to_email = request.user.email
    #send_email = EmailMessage(subject, message, to=['eshopsuppo@gmail.com'])
    #send_email.send()

    # Send order number and transation id back to sendDate method via JavaResponse
    data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
    return JsonResponse(data)


def order_completed(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotall = 0
        for i in ordered_products:
            subtotall += i.product_price * i.quantity
        subtotal = round(subtotall, 2)
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'shop/orders/order_completed/order_completed.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('shop:shop')
    