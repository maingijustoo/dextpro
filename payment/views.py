import json
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from stripe import Refund

from .models import Payment, PaymentMethod, MpesaPaymentRequest
from .services.mpesa_service import MpesaService
from .services.stripe_service import StripeService
from .forms import PaymentForm, PaymentSearchForm, RefundForm

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()

            if payment.payment_method.name == 'M-Pesa':
                mpesa_service = MpesaService()
                response = mpesa_service.initiate_stk_push(
                    phone_number=request.POST.get('phone_number'),
                    amount=payment.amount,
                    order_id=payment.order.id
                )
                # Handle response and save transaction details
                if response.get('ResponseCode') == '0':
                    MpesaPaymentRequest.objects.create(
                        payment=payment,
                        phone_number=request.POST.get('phone_number'),
                        checkout_request_id=response.get('CheckoutRequestID'),
                        is_completed=False
                    )
                    messages.success(request, "M-Pesa payment initiated successfully.")
                else:
                    messages.error(request, "M-Pesa payment initiation failed.")
            
            elif payment.payment_method.name == 'Stripe':
                stripe_service = StripeService()
                intent = stripe_service.create_payment_intent(amount=payment.amount)
                if intent:
                    payment.stripe_payment_intent = intent.id
                    payment.status = 'processing'
                    payment.save()
                    return JsonResponse({'client_secret': intent['client_secret']})
                else:
                    messages.error(request, "Stripe payment initiation failed.")

            return redirect('payment_list')
    else:
        form = PaymentForm()
    
    return render(request, 'payments/initiate_payment.html', {'form': form})

@csrf_exempt
def mpesa_callback(request):
    # Handle M-Pesa callback
    if request.method == 'POST':
        data = json.loads(request.body)
        checkout_request_id = data.get('CheckoutRequestID')
        response_code = data.get('ResponseCode')
        
        try:
            payment_request = MpesaPaymentRequest.objects.get(checkout_request_id=checkout_request_id)
            if response_code == '0':
                payment_request.is_completed = True
                payment_request.payment.status = 'completed'
                payment_request.payment.save()
                payment_request.save()
                # Additional logic for successful payment
            else:
                payment_request.response_description = data.get('ResponseDescription')
                payment_request.save()
        except MpesaPaymentRequest.DoesNotExist:
            pass

    return JsonResponse({'status': 'success'})

@login_required
def payment_detail(request, payment_id):
    """
    View payment details for a specific payment
    """
    # Fetch the payment, ensuring it belongs to the current user
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Fetch related refunds if any
    refunds = Refund.objects.filter(original_payment=payment)
    
    # Determine additional context based on payment method
    payment_details = {}
    if payment.payment_method == 'mpesa':
        try:
            mpesa_request = payment.mpesapaymentrequest_set.first()
            payment_details['mpesa_details'] = {
                'phone_number': mpesa_request.phone_number if mpesa_request else 'N/A',
                'checkout_request_id': mpesa_request.checkout_request_id if mpesa_request else 'N/A'
            }
        except:
            payment_details['mpesa_details'] = {}
    
    elif payment.payment_method == 'stripe':
        payment_details['stripe_details'] = {
            'payment_intent': payment.stripe_payment_intent
        }
    
    context = {
        'payment': payment,
        'order': payment.order,
        'refunds': refunds,
        'payment_details': payment_details
    }
    
    return render(request, 'payments/payment_detail.html', context)

def request_refund(request, payment_id):
    """
    Handle refund request for a specific payment
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Check if refund is possible
    if payment.status not in ['completed', 'processing']:
        messages.error(request, "This payment cannot be refunded.")
        return redirect('payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        form = RefundForm(request.POST, initial={'original_payment': payment})
        if form.is_valid():
            refund = form.save(commit=False)
            refund.original_payment = payment
            refund.user = request.user
            refund.save()
            
            # Update payment status
            payment.status = 'refunded'
            payment.save()
            
            messages.success(request, "Refund request submitted successfully.")
            return redirect('payment_detail', payment_id=payment.id)
    else:
        form = RefundForm(initial={'original_payment': payment})
    
    context = {
        'payment': payment,
        'form': form
    }
    
    return render(request, 'payments/request_refund.html', context)

@login_required
def payment_history(request):
    """
    View payment history for the current user
    """
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    # Apply filters if provided
    search_form = PaymentSearchForm(request.GET)
    if search_form.is_valid():
        start_date = search_form.cleaned_data.get('start_date')
        end_date = search_form.cleaned_data.get('end_date')
        payment_method = search_form.cleaned_data.get('payment_method')
        status = search_form.cleaned_data.get('status')
        min_amount = search_form.cleaned_data.get('min_amount')
        max_amount = search_form.cleaned_data.get('max_amount')
        
        if start_date:
            payments = payments.filter(payment_date__date__gte=start_date)
        if end_date:
            payments = payments.filter(payment_date__date__lte=end_date)
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
        if status:
            payments = payments.filter(status=status)
        if min_amount:
            payments = payments.filter(amount__gte=min_amount)
        if max_amount:
            payments = payments.filter(amount__lte=max_amount)
    
    context = {
        'payments': payments,
        'search_form': search_form
    }
    
    return render(request, 'payments/payment_history.html', context)