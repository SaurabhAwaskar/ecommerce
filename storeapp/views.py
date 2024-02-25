from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
# Create your views here.


def store(request):
	if request.user.is_authenticated:
		customer=request.user.customer
		order, created=Order.objects.get_or_create(customer=customer, complete=False)
		items=order.orderitem_set.all()
		cartItems=order.get_cart_items
	else:
		items=[]	
		order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartItems=order['get_cart_items']
	context = {'items':items,'order':order}
	products=Product.objects.all()
	context = {'products':products,'cartItems':cartItems }
	return render(request, 'store/store.html', context)

def cart(request):
	if request.user.is_authenticated:
		customer=request.user.customer
		order, created=Order.objects.get_or_create(customer=customer, complete=False)
		items=order.orderitem_set.all()
		cartItems=order.get_cart_items
	else:
		items=[]
		order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartItems=order['get_cart_items']
	context = {'items':items,'order':order,'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	if request.user.is_authenticated:
		customer=request.user.customer
		order, created=Order.objects.get_or_create(customer=customer, complete=False)
		items=order.orderitem_set.all()
		cartItems=order.get_cart_items
		client=razorpay.Client(auth=("rzp_test_L9jcigGS5amMiL","G1sRkAVSSPiHPs1Ljf4Z8LUs"))
		payment=client.order.create({'amount':order.get_cart_total*100,'currency':'INR','payment_capture':'1'})
		order.razorpay_order_id=payment['id']
		order.save()
	else:
		items=[]
		order={'get_cart_total':0,'get_cart_items':0}
		cartItems=order['get_cart_items']

	context = {'items':items,'order':order,'cartItems':cartItems,'shipping':False,'payment':payment}	
	return render(request, 'store/checkout.html', context)


def updateItem(request):
	data=json.loads(request.body)
	productId=data['productId']
	action=data['action']
	print('Action:',action)
	print('productId:',productId)
	customer=request.user.customer
	product=Product.objects.get(id=productId)
	order,creted=Order.objects.get_or_create(customer=customer,complete=False)
	orderItem,creted=OrderItem.objects.get_or_create(order=order,product=product)

	if action=='add':
		orderItem.quantity=orderItem.quantity+1
	elif action=='remove':
		orderItem.quantity=orderItem.quantity-1
	orderItem.save()

	if orderItem.quantity<=0:
		orderItem.delete()
	return JsonResponse('Item was added',safe=False)

def processOrder(request):

	transaction_id=datetime.datetime.now().timestamp()
	data=json.loads(request.body)
	
	if request.user.is_authenticated:
		customer=request.user.customer
		order,creted=Order.objects.get_or_create(customer=customer,complete=False)
		total=float(data['form']['total'])
		order.transaction_id=transaction_id

		if total==float(order.get_cart_total):
			order.complete=True
		order.save()

		if order.shipping==True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)
	else:
		print('User is not logged in..')
	return JsonResponse('Payment submitted',safe=False)